"""Parse uploaded files to plain text (txt, pdf)."""
from pathlib import Path


def parse_file(path: str | Path) -> str:
    """Parse file to plain text. Supports .txt and .pdf."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(str(path))
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        try:
            import pdfplumber
        except ImportError:
            raise RuntimeError("pdfplumber is required for PDF parsing. Install with: uv add pdfplumber")
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n\n".join(text_parts)
    raise ValueError(f"Unsupported file type: {suffix}. Use .txt or .pdf")
