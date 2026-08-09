"""
File upload models for NiralayOS.

Covers secure file storage metadata:
    UploadedFile

Binary files are stored on disk (or object storage).
This model stores the metadata and access control information.

The file is identified by a UUID-based storage path to prevent
enumeration and path traversal attacks.
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import AuditMixin, Base


class UploadedFile(AuditMixin, Base):
    """
    Metadata record for an uploaded file.

    The actual binary content lives at:
        {UPLOAD_PATH}/{storage_path}

    Access rules:
      - Public files (e.g. room photos, menu photos): accessible without auth
      - Private files (e.g. guest documents, expense receipts): require auth
    """

    __tablename__ = "uploaded_files"

    # Original filename as uploaded by the user
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)

    # Internal storage path (UUID-based, not guessable)
    storage_path: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        unique=True,
        comment="Relative path within UPLOAD_PATH directory",
    )

    # MIME type
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. image/jpeg, application/pdf",
    )

    # File size in bytes
    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # What type of entity this file belongs to
    entity_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment=(
            "room_type | menu_item | guest | expense | "
            "property | invoice | other"
        ),
    )
    entity_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="ID of the owning entity",
    )

    # Purpose / role within the entity
    purpose: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="photo | document | receipt | logo | invoice | other",
    )

    # Access control
    is_public: Mapped[bool] = mapped_column(
        Integer,
        nullable=False,
        default=False,
        comment="True = accessible without auth (e.g. room photos); False = requires auth",
    )

    uploaded_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="User who uploaded the file",
    )

    __table_args__ = (
        Index("ix_uploaded_files_entity", "entity_type", "entity_id"),
        Index("ix_uploaded_files_entity_type", "entity_type"),
        Index("ix_uploaded_files_uploaded_by", "uploaded_by"),
    )
