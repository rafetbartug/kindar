

from core.documents.cbz_document import CbzDocument
from core.documents.pdf_document import PdfDocument


SUPPORTED_DOCUMENTS = {
    ".pdf": PdfDocument,
    ".cbz": CbzDocument,
}


def create_document(document_path, cache_dir):
    suffix = document_path.suffix.lower()
    document_class = SUPPORTED_DOCUMENTS.get(suffix)

    if document_class is None:
        raise ValueError(f"Unsupported file type: {suffix}")

    return document_class(document_path, cache_dir)