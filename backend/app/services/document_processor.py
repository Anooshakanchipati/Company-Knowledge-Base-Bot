from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))

    page_texts = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            page_texts.append(text)

    return "\n".join(page_texts)


def extract_text_from_docx(file_path: Path) -> str:
    document = DocxDocument(str(file_path))

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def extract_text_from_txt(file_path: Path) -> str:
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(
            encoding="latin-1",
            errors="ignore",
        )


def extract_document_text(file_path_value: str) -> str:
    file_path = Path(file_path_value)

    if not file_path.exists():
        raise FileNotFoundError("The uploaded document file was not found")

    extension = file_path.suffix.lower()

    if extension == ".pdf":
        text = extract_text_from_pdf(file_path)

    elif extension == ".docx":
        text = extract_text_from_docx(file_path)

    elif extension == ".txt":
        text = extract_text_from_txt(file_path)

    else:
        raise ValueError("Unsupported document type")

    cleaned_text = "\n".join(
        line.strip()
        for line in text.splitlines()
        if line.strip()
    )

    if not cleaned_text:
        raise ValueError(
            "No readable text was found in the document"
        )

    return cleaned_text