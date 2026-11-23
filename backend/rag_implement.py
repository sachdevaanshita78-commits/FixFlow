import json
import re

MIN_SCORE = 0.45  # below this, treat the question as not covered (tune later)
TOP_K = 5

SYSTEM_PROMPT = """You are a customer-support assistant for Aurora Bank.
Answer ONLY using the numbered sources provided. Rules:
- Cite every fact with its source number in plain square brackets, like [1] or [2][3]. Never use any other citation format.
- If the sources do not contain the answer, reply exactly: INSUFFICIENT_EVIDENCE
- Do not use outside knowledge, and do not guess numbers, fees, limits or timelines.
- If the sources describe different options or conditions (for example temporary vs permanent, or app vs branch), say which applies to which. Do not merge them.
- Be concise and use plain language.

Answer format:
1. A direct answer to the question.
2. Then, if ANY source contains a deadline, an irreversible action, a liability or fee condition, or a safer/less drastic alternative related to the same situation, add a short section starting with "Also note:" listing each one with its citation. Read ALL the sources before writing this section. Omit the section only if no source has such information."""


def build_prompt(question: str, hits) -> str:
    blocks = []
    for i, hit in enumerate(hits, start=1):
        p = hit.payload
        blocks.append(f"[{i}] ({p['doc_code']} | {p['section']})\n{p['text']}")
    sources = "\n\n".join(blocks)
    return f"Sources:\n\n{sources}\n\nQuestion: {question}"


def call_llm(system: str, user: str) -> str:
    from groq import Groq
    from google.colab import userdata

    llm = Groq(api_key=userdata.get("GROQ_API_KEY"))
    response = llm.chat.completions.create(
        model="openai/gpt-oss-120b",
        temperature=0,
        max_tokens=3000,
        reasoning_effort="medium",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def normalize_citations(text: str) -> str:
    """Turn 【1†L1-L4】 style markers into [1], and add a space before markers."""
    text = re.sub(r"【(\d+)[^】]*】", r"[\1]", text)
    return re.sub(r"(\S)(\[\d+\])", r"\1 \2", text)


def answer(question: str) -> dict:
    hits = [h for h in search(question, top_k=TOP_K) if h.score >= MIN_SCORE]

    if not hits:
        return {"answer": None, "insufficient_evidence": True, "citations": []}

    text = call_llm(SYSTEM_PROMPT, build_prompt(question, hits))

    if not text or "INSUFFICIENT_EVIDENCE" in text:
        return {"answer": None, "insufficient_evidence": True, "citations": []}

    text = normalize_citations(text)

    # Keep only sources the answer actually cited (and that exist)
    cited = sorted({int(n) for n in re.findall(r"\[(\d+)\]", text) if 1 <= int(n) <= len(hits)})

    if not cited:
        return {"answer": None, "insufficient_evidence": True, "citations": []}

    citations = [
        {
            "n": n,
            "doc_code": hits[n - 1].payload["doc_code"],
            "section": hits[n - 1].payload["section"],
            "chunk_key": hits[n - 1].payload["chunk_key"],
            "score": round(hits[n - 1].score, 3),
        }
        for n in cited
    ]
    return {"answer": text, "insufficient_evidence": False, "citations": citations}


for q in [
    "What happens if I don't complete re-KYC?",
    "How do I block my lost debit card?",
    "What is the interest rate on Bitcoin deposits?",  # should be refused
]:
    print(f"\nQ: {q}")
    print(json.dumps(answer(q), indent=2, ensure_ascii=False))