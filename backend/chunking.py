
import re
import uuid


MAX_CHARS = 1200

HEADING_RE = re.compile(
    r"^(#{1,3})\s+(.+?)\s*$",
    re.MULTILINE,
)

DOC_ID_RE = re.compile(
    r"^\s*\**\s*Document ID:\s*\**\s*([A-Z0-9_-]+)",
    re.IGNORECASE | re.MULTILINE,
)

VERSION_RE = re.compile(
    r"^\s*\**\s*Version:\s*\**\s*([\w.-]+)",
    re.IGNORECASE | re.MULTILINE,
)


def extract_doc_info(text: str) -> dict:
    """Extract the title, document code, and version."""

    title = ""

    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)

        if match:
            title = match.group(1).strip()
            break

    head = text[:2000]
    code = DOC_ID_RE.search(head)
    version = VERSION_RE.search(head)

    return {
        "doc_title": title,
        "doc_code": code.group(1) if code else "",
        "doc_version": version.group(1) if version else "",
    }


def split_into_sections(text: str) -> list[tuple[str, str]]:
    """Split text at Markdown H2 and H3 headings."""

    sections = []
    current_heading = "Overview"
    current_lines = []

    for line in text.splitlines():
        match = HEADING_RE.match(line)

        # H1 is the document title; H2/H3 start new sections.
        if match and len(match.group(1)) >= 2:
            body = "\n".join(current_lines).strip()

            if body:
                sections.append((current_heading, body))

            current_heading = match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    body = "\n".join(current_lines).strip()

    if body:
        sections.append((current_heading, body))

    return sections or [("Overview", text.strip())]


def split_long_body(body: str, limit: int) -> list[str]:
    """Split long sections by paragraphs, then by lines if necessary."""

    blocks = [
        block.strip()
        for block in re.split(r"\n\s*\n", body)
        if block.strip()
    ]

    expanded = []

    for block in blocks:
        if len(block) <= limit:
            expanded.append(block)
            continue

        current = ""

        for line in block.splitlines():
            while len(line) > limit:
                if current:
                    expanded.append(current)
                    current = ""

                expanded.append(line[:limit])
                line = line[limit:]

            if current and len(current) + len(line) + 1 > limit:
                expanded.append(current)
                current = line
            else:
                current = f"{current}\n{line}" if current else line

        if current:
            expanded.append(current)

    pieces = []
    current = ""

    for block in expanded:
        candidate = f"{current}\n\n{block}" if current else block

        if current and len(candidate) > limit:
            pieces.append(current)
            current = block
        else:
            current = candidate

    if current:
        pieces.append(current)

    return pieces


def chunk_document(
    document: dict,
    max_chars: int = MAX_CHARS,
) -> list[dict]:
    """Create deterministic, heading-aware chunks for one document."""

    text = document["text"].strip()
    base_meta = document["metadata"]

    if not text:
        return []

    if max_chars <= 0:
        raise ValueError("max_chars must be positive")

    info = extract_doc_info(text)

    document_id = str(base_meta["document_id"])
    tenant_id = str(base_meta["tenant_id"])

    chunks = []
    chunk_index = 0

    for heading, body in split_into_sections(text):
        prefix = (
            f"{info['doc_title']} > {heading}"
            if info["doc_title"]
            else heading
        )

        budget = max(200, max_chars - len(prefix) - 2)

        for piece in split_long_body(body, budget):
            chunk_key = f"{document_id}::{chunk_index}"

            point_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"fixflow:{tenant_id}:{chunk_key}",
                )
            )

            chunks.append(
                {
                    "id": point_id,
                    "text": f"{prefix}\n\n{piece}",
                    "metadata": {
                        **base_meta,
                        **info,
                        "tenant_id": tenant_id,
                        "document_id": document_id,
                        "section": heading,
                        "chunk_index": chunk_index,
                        "chunk_key": chunk_key,
                    },
                }
            )

            chunk_index += 1

    return chunks


def chunk_all(
    documents: list[dict],
    max_chars: int = MAX_CHARS,
) -> list[dict]:
    """Chunk multiple documents using the Colab-compatible logic."""

    result = []

    for document in documents:
        result.extend(chunk_document(document, max_chars))

    return result
