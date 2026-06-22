from io import BytesIO

import PyPDF2


class PDFReader:
    def extract_text(self, pdf_file) -> str:
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(page.strip() for page in pages if page.strip())
        except Exception as exc:
            raise ValueError("The PDF could not be parsed. Try a text-based PDF instead of a scanned image.") from exc

    def extract_text_from_bytes(self, file_bytes: bytes) -> str:
        return self.extract_text(BytesIO(file_bytes))


def extract_text(pdf_file) -> str:
    return PDFReader().extract_text(pdf_file)
