
import json
import io
from pathlib import Path

import pandas as pd
import pymupdf
from bs4 import BeautifulSoup
from docx import Document


SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".txt", ".md",
    ".html", ".htm", ".csv", ".xlsx", ".json",
}


def extract_document_bytes(
    content: bytes,
    filename: str,
) -> str:
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")

    if not content:
        raise ValueError("The uploaded document is empty.")

    stream = io.BytesIO(content)

    if extension == ".pdf":
        pages = []

        with pymupdf.open(stream=stream, filetype="pdf") as pdf:
            for page_number, page in enumerate(pdf, start=1):
                text = page.get_text("text")

                if text.strip():
                    pages.append(f"[Page {page_number}]\n{text}")

        extracted = "\n\n".join(pages)

    elif extension == ".docx":
        doc = Document(stream)
        sections = []

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                sections.append(paragraph.text)

        for table_number, table in enumerate(doc.tables, start=1):
            sections.append(f"[Table {table_number}]")

            for row in table.rows:
                sections.append(
                    " | ".join(cell.text.strip() for cell in row.cells)
                )

        extracted = "\n\n".join(sections)

    elif extension in {".txt", ".md"}:
        extracted = content.decode("utf-8-sig", errors="replace")

    elif extension in {".html", ".htm"}:
        soup = BeautifulSoup(
            content.decode("utf-8", errors="replace"),
            "html.parser",
        )

        for element in soup(
            ["script", "style", "noscript", "nav", "footer"]
        ):
            element.decompose()

        extracted = soup.get_text(separator="\n", strip=True)

    elif extension == ".csv":
        df = pd.read_csv(io.BytesIO(content), dtype=str).fillna("")
        extracted = df.to_csv(index=False)

    elif extension == ".xlsx":
        sheets = pd.read_excel(
            io.BytesIO(content),
            sheet_name=None,
            dtype=str,
            engine="openpyxl",
        )

        sections = []

        for sheet_name, df in sheets.items():
            sections.append(f"[Sheet: {sheet_name}]")
            sections.append(df.fillna("").to_csv(index=False))

        extracted = "\n\n".join(sections)

    elif extension == ".json":
        data = json.loads(content.decode("utf-8-sig"))
        extracted = json.dumps(data, ensure_ascii=False, indent=2)

    else:
        raise ValueError(f"Unsupported file type: {extension}")

    if not extracted.strip():
        raise ValueError("No extractable text found in the document.")

    return extracted


def make_document(
    content: bytes,
    filename: str,
    document_id: str,
    tenant_id: str,
) -> dict:
    """Convert one downloaded FixFlow file into the RAG input format."""
    text = extract_document_bytes(content, filename)

    return {
        "text": text,
        "metadata": {
            "document_id": str(document_id),
            "tenant_id": str(tenant_id),
            "source": Path(filename).name,
            "file_type": Path(filename).suffix.lower(),
            "character_count": len(text),
        },
    }
