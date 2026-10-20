import io
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

MAX_MB = 10
MAX_FILES = 5

def validate_pdf(filename, size_bytes, max_mb=MAX_MB):
    # returns (ok, message)
    if not filename.lower().endswith(".pdf"):
        return False, f"{filename}: only PDF files are allowed."
    if size_bytes > max_mb * 1024 * 1024:
        return False, f"{filename}: larger than {max_mb} MB."
    return True, "OK"

def load_pdf(source, filename):
    # Read every page with pypdf. Keep document name + page number as metadata. Skip empty pages safely.
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)
    reader = PdfReader(source)
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        try:
            text = (page.extract_text() or "").strip()
        except Exception:
            text = ""
        if text:
            pages.append({"text": text, "source": filename, "page": number})
    return pages

def chunk_pages(pages, chunk_size=800, chunk_overlap=120):
    # Split each page separately so the page number of every chunk stays exact.
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap,
                                              separators=["\n\n", "\n", ". ", " ", ""])
    chunks = []
    for p in pages:
        for piece in splitter.split_text(p["text"]):
            chunks.append({"text": piece, "source": p["source"], "page": p["page"], "chunk_id": len(chunks)})
    return chunks
