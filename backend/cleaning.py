
import re
import unicodedata


# Remove invisible characters that are safe to drop.
# Preserve ZWNJ and ZWJ because they can be meaningful in Indic scripts.
REMOVABLE_INVISIBLES = {"\u200b", "\ufeff", "\u00ad"}


def clean_text(text: str) -> str:
    """Normalize extracted document text consistently before chunking."""

    if not text:
        return ""

    # Normalize Unicode.
    text = unicodedata.normalize("NFC", text)

    # Normalize line endings before filtering control characters.
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Convert PDF page breaks into paragraph breaks.
    text = text.replace("\x0c", "\n\n")

    cleaned_chars = []

    for char in text:
        if char in REMOVABLE_INVISIBLES:
            continue

        category = unicodedata.category(char)

        if category == "Zs":
            cleaned_chars.append(" ")
        elif char in "\n\t" or category != "Cc":
            cleaned_chars.append(char)

    text = "".join(cleaned_chars)

    # Collapse repeated spaces and tabs without removing paragraph breaks.
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces at the beginning and end of lines.
    text = re.sub(r" *\n *", "\n", text)

    # Limit excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
