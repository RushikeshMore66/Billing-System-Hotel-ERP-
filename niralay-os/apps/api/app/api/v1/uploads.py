"""
File Upload Router for NiralayOS.

Provides secure authenticated file upload and retrieval.
Files are stored on local disk under UPLOAD_PATH.
Private files require authentication to access.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user, get_db
from app.core.constants import UPLOAD_ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_BYTES
from app.core.settings import settings
from app.models.file_upload import UploadedFile
from app.models.user import User

router = APIRouter(prefix="/uploads", tags=["File Uploads"])


class UploadedFileOut(BaseModel):
    id: int
    original_filename: str
    storage_path: str
    mime_type: str
    file_size: int
    entity_type: str | None = None
    entity_id: int | None = None
    purpose: str | None = None
    is_public: bool

    class Config:
        from_attributes = True


def _get_upload_dir() -> Path:
    upload_dir = Path(settings.UPLOAD_PATH)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


@router.post(
    "",
    response_model=UploadedFileOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: UploadFile = File(...),
    entity_type: str | None = Query(None),
    entity_id: int | None = Query(None),
    purpose: str | None = Query(None, description="photo | document | receipt | logo | other"),
    is_public: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UploadedFileOut:
    """Upload a file and create a metadata record."""

    # Validate filename extension
    original_filename = file.filename or "upload"
    ext = Path(original_filename).suffix.lower()
    if ext not in UPLOAD_ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File type '{ext}' is not allowed. Allowed: {', '.join(UPLOAD_ALLOWED_EXTENSIONS)}",
        )

    # Read content and validate size
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB",
        )

    # Generate secure storage path
    unique_name = f"{uuid.uuid4().hex}{ext}"
    upload_dir = _get_upload_dir()
    file_path = upload_dir / unique_name

    # Write to disk
    file_path.write_bytes(content)

    # Create metadata record
    uploaded_file = UploadedFile(
        original_filename=original_filename,
        storage_path=unique_name,
        mime_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        entity_type=entity_type,
        entity_id=entity_id,
        purpose=purpose,
        is_public=is_public,
        uploaded_by=current_user.id,
    )
    db.add(uploaded_file)
    db.flush()
    db.commit()

    return UploadedFileOut.model_validate(uploaded_file)


@router.get("/{file_id}")
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FileResponse:
    """Retrieve an uploaded file (authenticated)."""
    from sqlalchemy import select

    record = db.scalars(select(UploadedFile).where(UploadedFile.id == file_id)).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    upload_dir = _get_upload_dir()
    file_path = upload_dir / record.storage_path

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File data not found on disk",
        )

    return FileResponse(
        path=str(file_path),
        media_type=record.mime_type,
        filename=record.original_filename,
    )


@router.get("/public/{file_id}")
def get_public_file(
    file_id: int,
    db: Session = Depends(get_db),
) -> FileResponse:
    """Retrieve a public file (no authentication required)."""
    from sqlalchemy import select

    record = db.scalars(select(UploadedFile).where(UploadedFile.id == file_id)).first()
    if not record or not record.is_public:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    upload_dir = _get_upload_dir()
    file_path = upload_dir / record.storage_path

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File data not found on disk",
        )

    return FileResponse(
        path=str(file_path),
        media_type=record.mime_type,
        filename=record.original_filename,
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """Delete an uploaded file and its disk content."""
    from sqlalchemy import select

    record = db.scalars(select(UploadedFile).where(UploadedFile.id == file_id)).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Remove from disk
    upload_dir = _get_upload_dir()
    file_path = upload_dir / record.storage_path
    if file_path.exists():
        file_path.unlink()

    db.delete(record)
    db.commit()
