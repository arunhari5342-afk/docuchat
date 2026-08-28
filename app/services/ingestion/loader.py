from pathlib import Path

from pypdf import PdfReader


def load_text_file(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".txt":
        raise ValueError("Only .txt files are supported by this loader")

    return path.read_text(encoding="utf-8")


def load_pdf_file(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only .pdf files are supported by this loader")

    reader = PdfReader(str(path))

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def load_document(file_path: str) -> str:
    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".txt":
        return load_text_file(file_path)

    if extension == ".pdf":
        return load_pdf_file(file_path)

    raise ValueError(
        f"Unsupported file type: {extension}. "
        "Only .txt and .pdf files are supported."
    )