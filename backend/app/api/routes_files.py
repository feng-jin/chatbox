"""File upload API."""
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.app.core.config import MAX_FILE_SIZE_MB, UPLOADS_DIR
from backend.app.db import repo
from backend.app.services import rag_service

router = APIRouter(prefix="/api", tags=["files"])

MAX_BYTES = int(MAX_FILE_SIZE_MB * 1024 * 1024)
ALLOWED_SUFFIXES = {".txt", ".pdf"}


@router.post("/files")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="filename required")
    safe_name = Path(file.filename).name
    suffix = Path(safe_name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt or .pdf")
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=400, detail=f"File too large (max {MAX_FILE_SIZE_MB}MB)")
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = UPLOADS_DIR / f"{uuid.uuid4().hex}_{safe_name}"
    out_path.write_bytes(content)
    try:
        rec = repo.create_file(filename=safe_name, path=str(out_path), mime_type=file.content_type)
    except Exception as e:
        out_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(e))
    indexed = True
    try:
        rag_service.index_file(file_id=rec["id"], file_path=str(out_path))
    except Exception:
        # Keep file record and path; indexing can be retried later
        indexed = False
    return {
        "file_id": rec["id"],
        "filename": rec["filename"],
        "status": "indexed" if indexed else "uploaded",
        "indexed": indexed,
    }
