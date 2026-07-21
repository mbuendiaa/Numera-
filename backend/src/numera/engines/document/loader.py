from pathlib import Path

from fastapi import UploadFile


class DocumentLoader:
    def save_upload(self, *, upload_dir: Path, company_id: str, file: UploadFile) -> Path:
        company_dir = upload_dir / company_id
        company_dir.mkdir(parents=True, exist_ok=True)
        target = company_dir / file.filename
        with target.open("wb") as buffer:
            buffer.write(file.file.read())
        return target
