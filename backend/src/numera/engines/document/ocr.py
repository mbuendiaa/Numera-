from pathlib import Path

import pytesseract
from PIL import Image
from pypdf import PdfReader

from numera.core.config import settings


class TextExtractor:
    def extract_text(self, path: Path, content_type: str) -> tuple[str, list[str]]:
        suffix = path.suffix.lower()

        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

        if suffix == ".txt":
            return path.read_text(encoding="utf-8", errors="ignore"), ["Plain text file detected."]

        if suffix == ".pdf":
            text = self._extract_pdf_text(path)
            if text:
                return text, ["PDF text layer extracted with pypdf."]
            return "", ["PDF has no readable text layer."]

        if suffix in {".jpg", ".jpeg", ".png", ".tif", ".tiff"}:
            text = self._extract_image_text(path)
            if text.startswith("OCR_ERROR"):
                return text, [text]
            return text, ["Image OCR completed with Tesseract."]

        return "", ["Unsupported file type for text extraction."]

    def _extract_pdf_text(self, path: Path) -> str:
        try:
            reader = PdfReader(str(path))
            return "\n".join([(page.extract_text() or "") for page in reader.pages]).strip()
        except Exception:
            return ""

    def _extract_image_text(self, path: Path) -> str:
        try:
            image = Image.open(path)
            return pytesseract.image_to_string(image, lang="spa+eng").strip()
        except Exception as exc:
            return f"OCR_ERROR: {exc}"
