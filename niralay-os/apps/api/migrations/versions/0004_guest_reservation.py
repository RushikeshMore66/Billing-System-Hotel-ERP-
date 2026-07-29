"""guest_and_reservation

Revision ID: 0004_guest_reservation
Revises: 0003_property_config
Create Date: 2026-07-18

Creates tables:
- guests
- reservations
- reservation_status_history
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "0004_guest_reservation"
down_revision: str | None = "0003_property_config"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def _audit_cols() -> list[sa.Column]:
    return [
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False,
                  server_default=sa.text("gen_random_uuid()"), unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
    ]


def upgrade() -> None:
    # 1. Guests
    op.create_table(
        "guests",
        *_audit_cols(),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True, index=True),
        sa.Column("phone", sa.String(50), nullable=True, index=True),
        sa.Column("id_type_id", sa.Integer, sa.ForeignKey("guest_id_types.id", ondelete="SET NULL"), nullable=True),
        sa.Column("id_number", sa.String(100), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("nationality", sa.String(100), nullable=True, server_default="Indian"),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # 2. Reservations
    op.create_table(
        "reservations",
        *_audit_cols(),
        sa.Column("reservation_number", sa.String(50), unique=True, index=True, nullable=False),
        sa.Column("guest_id", sa.Integer, sa.ForeignKey("guests.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("room_id", sa.Integer, sa.ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("room_type_id", sa.Integer, sa.ForeignKey("room_types.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("check_in_date", sa.Date(), nullable=False),
        sa.Column("check_out_date", sa.Date(), nullable=False),
        sa.Column("nights", sa.Integer, nullable=False, server_default="1"),
        sa.Column("adults", sa.Integer, nullable=False, server_default="1"),
        sa.Column("children", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(50), nullable=False, server_default="PENDING", index=True),
        sa.Column("source", sa.String(50), nullable=False, server_default="DIRECT"),
        sa.Column("rate_plan_id", sa.Integer, sa.ForeignKey("rate_plans.id", ondelete="SET NULL"), nullable=True),
        sa.Column("base_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("tax_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("advance_paid", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("special_requests", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # 3. Reservation Status History
    op.create_table(
        "reservation_status_history",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("reservation_id", sa.Integer, sa.ForeignKey("reservations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("from_status", sa.String(50), nullable=True),
        sa.Column("to_status", sa.String(50), nullable=False),
        sa.Column("changed_by", sa.String(255), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("remarks", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("reservation_status_history")
    op.drop_table("reservations")
    op.drop_table("guests")
