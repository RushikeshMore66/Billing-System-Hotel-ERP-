"""property_config_sprint3

Revision ID: 0003_property_config
Revises: 0002_identity_platform
Create Date: 2026-07-17

Creates all Sprint 3 Property Configuration Platform tables:
    property_profiles
    floors
    amenities
    bed_types
    room_types, room_type_amenities (M2M), room_type_images
    rooms
    taxes
    payment_methods
    currencies
    seasons
    rate_plans, rate_plan_season_rates
    restaurant_categories
    menu_categories
    kitchen_stations
    menu_items, menu_item_modifiers (M2M)
    menu_modifiers, menu_modifier_options
    restaurant_tables
    departments
    designations
    guest_id_types
    business_settings

Seeds system amenities, bed types, payment methods, departments,
designations, guest ID types, currencies, and default business settings.
"""

from __future__ import annotations

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "0003_property_config"
down_revision: str | None = "0002_identity_platform"
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def _audit_cols() -> list[sa.Column]:
    """Return the standard AuditMixin columns for every table."""
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
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
    ]


def upgrade() -> None:
    # ------------------------------------------------------------------
    # property_profiles
    # ------------------------------------------------------------------
    op.create_table(
        "property_profiles",
        *_audit_cols(),
        sa.Column("hotel_name", sa.String(255), nullable=False, server_default="My Hotel"),
        sa.Column("logo_url", sa.String(512), nullable=True),
        sa.Column("address_line1", sa.String(255), nullable=True),
        sa.Column("address_line2", sa.String(255), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("country", sa.String(100), nullable=True, server_default="India"),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("email", sa.String(320), nullable=True),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("website", sa.String(512), nullable=True),
        sa.Column("gst_number", sa.String(15), nullable=True),
        sa.Column("pan_number", sa.String(10), nullable=True),
        sa.Column("currency_code", sa.String(3), nullable=False, server_default="INR"),
        sa.Column("timezone", sa.String(60), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("check_in_time", sa.Time(), nullable=True),
        sa.Column("check_out_time", sa.Time(), nullable=True),
        sa.Column("invoice_prefix", sa.String(10), nullable=False, server_default="INV"),
        sa.Column("business_registration_number", sa.String(100), nullable=True),
        sa.Column("business_registration_details", sa.Text, nullable=True),
        sa.Column("star_rating", sa.Integer, nullable=True),
    )

    # ------------------------------------------------------------------
    # floors
    # ------------------------------------------------------------------
    op.create_table(
        "floors",
        *_audit_cols(),
        sa.Column("floor_number", sa.Integer, nullable=False),
        sa.Column("floor_name", sa.String(100), nullable=False),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.UniqueConstraint("floor_number", name="uq_floors_floor_number"),
    )
    op.create_index("ix_floors_status", "floors", ["status"])
    op.create_index("ix_floors_display_order", "floors", ["display_order"])

    # ------------------------------------------------------------------
    # amenities
    # ------------------------------------------------------------------
    op.create_table(
        "amenities",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="false"),
        sa.UniqueConstraint("name", name="uq_amenities_name"),
    )

    # ------------------------------------------------------------------
    # bed_types
    # ------------------------------------------------------------------
    op.create_table(
        "bed_types",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="false"),
        sa.UniqueConstraint("name", name="uq_bed_types_name"),
    )

    # ------------------------------------------------------------------
    # room_types
    # ------------------------------------------------------------------
    op.create_table(
        "room_types",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("base_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("weekend_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("max_occupancy", sa.Integer, nullable=False, server_default="2"),
        sa.Column("extra_bed_allowed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("extra_bed_charge", sa.Numeric(12, 2), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.UniqueConstraint("name", name="uq_room_types_name"),
    )

    # room_type_amenities (M2M)
    op.create_table(
        "room_type_amenities",
        sa.Column("room_type_id", sa.Integer,
                  sa.ForeignKey("room_types.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("amenity_id", sa.Integer,
                  sa.ForeignKey("amenities.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("added_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )

    # room_type_images
    op.create_table(
        "room_type_images",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("room_type_id", sa.Integer,
                  sa.ForeignKey("room_types.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("image_url", sa.String(512), nullable=False),
        sa.Column("caption", sa.String(255), nullable=True),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
    )

    # ------------------------------------------------------------------
    # rooms
    # ------------------------------------------------------------------
    op.create_table(
        "rooms",
        *_audit_cols(),
        sa.Column("room_number", sa.String(20), nullable=False),
        sa.Column("floor_id", sa.Integer,
                  sa.ForeignKey("floors.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("room_type_id", sa.Integer,
                  sa.ForeignKey("room_types.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("capacity", sa.Integer, nullable=False, server_default="2"),
        sa.Column("view", sa.String(100), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="available"),
        sa.Column("housekeeping_status", sa.String(30), nullable=False, server_default="clean"),
        sa.Column("maintenance_status", sa.String(30), nullable=False, server_default="operational"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.UniqueConstraint("room_number", name="uq_rooms_room_number"),
    )
    op.create_index("ix_rooms_status", "rooms", ["status"])
    op.create_index("ix_rooms_housekeeping_status", "rooms", ["housekeeping_status"])
    op.create_index("ix_rooms_maintenance_status", "rooms", ["maintenance_status"])

    # ------------------------------------------------------------------
    # taxes
    # ------------------------------------------------------------------
    op.create_table(
        "taxes",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("tax_type", sa.String(20), nullable=False, server_default="percentage"),
        sa.Column("rate", sa.Numeric(10, 4), nullable=False),
        sa.Column("is_inclusive", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("applies_to", sa.String(50), nullable=False, server_default="all"),
        sa.Column("description", sa.Text, nullable=True),
        sa.UniqueConstraint("code", name="uq_taxes_code"),
    )
    op.create_index("ix_taxes_is_active", "taxes", ["is_active"])

    # ------------------------------------------------------------------
    # payment_methods
    # ------------------------------------------------------------------
    op.create_table(
        "payment_methods",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("payment_type", sa.String(50), nullable=False),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("requires_reference", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.UniqueConstraint("code", name="uq_payment_methods_code"),
    )

    # ------------------------------------------------------------------
    # currencies
    # ------------------------------------------------------------------
    op.create_table(
        "currencies",
        *_audit_cols(),
        sa.Column("code", sa.String(3), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("symbol", sa.String(5), nullable=False),
        sa.Column("exchange_rate", sa.Numeric(16, 6), nullable=False, server_default="1.0"),
        sa.Column("decimal_places", sa.Integer, nullable=False, server_default="2"),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.UniqueConstraint("code", name="uq_currencies_code"),
    )

    # ------------------------------------------------------------------
    # seasons
    # ------------------------------------------------------------------
    op.create_table(
        "seasons",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("priority", sa.Integer, nullable=False, server_default="0"),
        sa.Column("description", sa.Text, nullable=True),
    )
    op.create_index("ix_seasons_start_date", "seasons", ["start_date"])
    op.create_index("ix_seasons_end_date", "seasons", ["end_date"])

    # ------------------------------------------------------------------
    # rate_plans
    # ------------------------------------------------------------------
    op.create_table(
        "rate_plans",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("meal_plan", sa.String(20), nullable=False, server_default="EP"),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("min_stay_nights", sa.Integer, nullable=False, server_default="1"),
        sa.Column("max_stay_nights", sa.Integer, nullable=True),
        sa.Column("cancellation_policy", sa.Text, nullable=True),
        sa.UniqueConstraint("code", name="uq_rate_plans_code"),
    )

    op.create_table(
        "rate_plan_season_rates",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("rate_plan_id", sa.Integer,
                  sa.ForeignKey("rate_plans.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("room_type_id", sa.Integer,
                  sa.ForeignKey("room_types.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("season_id", sa.Integer,
                  sa.ForeignKey("seasons.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("price_per_night", sa.Numeric(12, 2), nullable=False),
        sa.Column("weekend_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("extra_person_charge", sa.Numeric(12, 2), nullable=True),
        sa.UniqueConstraint("rate_plan_id", "room_type_id", "season_id",
                            name="uq_rate_plan_season_rates"),
    )

    # ------------------------------------------------------------------
    # restaurant_categories
    # ------------------------------------------------------------------
    op.create_table(
        "restaurant_categories",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("color", sa.String(7), nullable=True),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.UniqueConstraint("name", name="uq_restaurant_categories_name"),
    )
    op.create_index("ix_restaurant_categories_display_order", "restaurant_categories", ["display_order"])

    # ------------------------------------------------------------------
    # menu_categories
    # ------------------------------------------------------------------
    op.create_table(
        "menu_categories",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("restaurant_category_id", sa.Integer,
                  sa.ForeignKey("restaurant_categories.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("parent_id", sa.Integer,
                  sa.ForeignKey("menu_categories.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("image_url", sa.String(512), nullable=True),
    )
    op.create_index("ix_menu_categories_display_order", "menu_categories", ["display_order"])

    # ------------------------------------------------------------------
    # kitchen_stations
    # ------------------------------------------------------------------
    op.create_table(
        "kitchen_stations",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("printer_name", sa.String(100), nullable=True),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("name", name="uq_kitchen_stations_name"),
    )

    # ------------------------------------------------------------------
    # menu_items
    # ------------------------------------------------------------------
    op.create_table(
        "menu_items",
        *_audit_cols(),
        sa.Column("item_code", sa.String(30), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("menu_category_id", sa.Integer,
                  sa.ForeignKey("menu_categories.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("kitchen_station_id", sa.Integer,
                  sa.ForeignKey("kitchen_stations.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("tax_id", sa.Integer,
                  sa.ForeignKey("taxes.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("cost_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("food_type", sa.String(20), nullable=False, server_default="veg"),
        sa.Column("is_available", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("prep_time_minutes", sa.Integer, nullable=True),
        sa.Column("image_url", sa.String(512), nullable=True),
        sa.Column("allergens", sa.String(255), nullable=True),
        sa.Column("calories", sa.Integer, nullable=True),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("item_code", name="uq_menu_items_item_code"),
    )
    op.create_index("ix_menu_items_food_type", "menu_items", ["food_type"])
    op.create_index("ix_menu_items_is_available", "menu_items", ["is_available"])

    # ------------------------------------------------------------------
    # menu_modifiers
    # ------------------------------------------------------------------
    op.create_table(
        "menu_modifiers",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("modifier_type", sa.String(30), nullable=False, server_default="single"),
        sa.Column("is_required", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("min_selections", sa.Integer, nullable=False, server_default="0"),
        sa.Column("max_selections", sa.Integer, nullable=True),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("name", name="uq_menu_modifiers_name"),
    )

    op.create_table(
        "menu_modifier_options",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("modifier_id", sa.Integer,
                  sa.ForeignKey("menu_modifiers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("price_impact", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
    )

    # menu_item_modifiers (M2M)
    op.create_table(
        "menu_item_modifiers",
        sa.Column("menu_item_id", sa.Integer,
                  sa.ForeignKey("menu_items.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("menu_modifier_id", sa.Integer,
                  sa.ForeignKey("menu_modifiers.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("linked_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )

    # ------------------------------------------------------------------
    # restaurant_tables
    # ------------------------------------------------------------------
    op.create_table(
        "restaurant_tables",
        *_audit_cols(),
        sa.Column("table_number", sa.String(20), nullable=False),
        sa.Column("capacity", sa.Integer, nullable=False, server_default="4"),
        sa.Column("section", sa.String(100), nullable=True),
        sa.Column("location_type", sa.String(20), nullable=False, server_default="indoor"),
        sa.Column("status", sa.String(20), nullable=False, server_default="available"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.UniqueConstraint("table_number", name="uq_restaurant_tables_table_number"),
    )
    op.create_index("ix_restaurant_tables_status", "restaurant_tables", ["status"])
    op.create_index("ix_restaurant_tables_section", "restaurant_tables", ["section"])

    # ------------------------------------------------------------------
    # departments
    # ------------------------------------------------------------------
    op.create_table(
        "departments",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("code", name="uq_departments_code"),
        sa.UniqueConstraint("name", name="uq_departments_name"),
    )

    # ------------------------------------------------------------------
    # designations
    # ------------------------------------------------------------------
    op.create_table(
        "designations",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("department_id", sa.Integer,
                  sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("code", name="uq_designations_code"),
    )

    # ------------------------------------------------------------------
    # guest_id_types
    # ------------------------------------------------------------------
    op.create_table(
        "guest_id_types",
        *_audit_cols(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("is_system", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("requires_expiry", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("display_order", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("code", name="uq_guest_id_types_code"),
        sa.UniqueConstraint("name", name="uq_guest_id_types_name"),
    )

    # ------------------------------------------------------------------
    # business_settings
    # ------------------------------------------------------------------
    op.create_table(
        "business_settings",
        *_audit_cols(),
        sa.Column("invoice_number_format", sa.String(100), nullable=False,
                  server_default="INV-{YYYY}-{MM}-{SEQ}"),
        sa.Column("reservation_number_format", sa.String(100), nullable=False,
                  server_default="RES-{YYYY}-{SEQ}"),
        sa.Column("invoice_sequence_start", sa.Integer, nullable=False, server_default="1"),
        sa.Column("reservation_sequence_start", sa.Integer, nullable=False, server_default="1"),
        sa.Column("timezone", sa.String(60), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("date_format", sa.String(30), nullable=False, server_default="DD/MM/YYYY"),
        sa.Column("time_format", sa.String(10), nullable=False, server_default="12h"),
        sa.Column("currency_format", sa.String(20), nullable=False, server_default="symbol_before"),
        sa.Column("decimal_precision", sa.Integer, nullable=False, server_default="2"),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("auto_backup_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("auto_backup_frequency", sa.String(20), nullable=False, server_default="daily"),
        sa.Column("backup_retention_days", sa.Integer, nullable=False, server_default="30"),
        sa.Column("backup_storage_path", sa.String(512), nullable=True),
        sa.Column("tax_inclusive_by_default", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("allow_partial_payment", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("minimum_advance_payment_pct", sa.Integer, nullable=False, server_default="0"),
        sa.Column("additional_notes", sa.Text, nullable=True),
    )

    # ==================================================================
    # SEED DATA
    # ==================================================================
    now = datetime.now(timezone.utc)

    # ── System amenities ─────────────────────────────────────────────
    op.bulk_insert(
        sa.table(
            "amenities",
            sa.column("name"), sa.column("icon"), sa.column("is_system"),
            sa.column("is_active"), sa.column("created_at"), sa.column("updated_at"),
        ),
        [
            {"name": "WiFi", "icon": "wifi", "is_system": True, "is_active": True,
             "created_at": now, "updated_at": now},
            {"name": "Air Conditioning", "icon": "wind", "is_system": True, "is_active": True,
             "created_at": now, "updated_at": now},
            {"name": "Television", "icon": "tv", "is_system": True, "is_active": True,
             "created_at": now, "updated_at": now},
            {"name": "Parking", "icon": "car", "is_system": True, "is_active": True,
             "created_at": now, "updated_at": now},
            {"name": "Breakfast Included", "icon": "coffee", "is_system": True, "is_active": True,
             "created_at": now, "updated_at": now},
            {"name": "Laundry Service", "icon": "shirt", "is_system": True, "is_active": True,
             "created_at": now, "updated_at": now},
            {"name": "Swimming Pool", "icon": "waves", "is_system": False, "is_active": True,
             "created_at": now, "updated_at": now},
            {"name": "Gym", "icon": "dumbbell", "is_system": False, "is_active": True,
             "created_at": now, "updated_at": now},
            {"name": "Spa", "icon": "sparkles", "is_system": False, "is_active": True,
             "created_at": now, "updated_at": now},
            {"name": "Room Service", "icon": "bell", "is_system": True, "is_active": True,
             "created_at": now, "updated_at": now},
        ],
    )

    # ── System bed types ─────────────────────────────────────────────
    op.bulk_insert(
        sa.table(
            "bed_types",
            sa.column("name"), sa.column("description"), sa.column("is_system"),
            sa.column("is_active"), sa.column("created_at"), sa.column("updated_at"),
        ),
        [
            {"name": "Single", "description": "Single bed (90×190 cm)", "is_system": True,
             "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Double", "description": "Double bed (140×190 cm)", "is_system": True,
             "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Queen", "description": "Queen-size bed (160×200 cm)", "is_system": True,
             "is_active": True, "created_at": now, "updated_at": now},
            {"name": "King", "description": "King-size bed (180×200 cm)", "is_system": True,
             "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Twin", "description": "Two single beds", "is_system": True,
             "is_active": True, "created_at": now, "updated_at": now},
        ],
    )

    # ── System payment methods ────────────────────────────────────────
    op.bulk_insert(
        sa.table(
            "payment_methods",
            sa.column("name"), sa.column("code"), sa.column("payment_type"),
            sa.column("is_system"), sa.column("requires_reference"), sa.column("icon"),
            sa.column("is_active"), sa.column("created_at"), sa.column("updated_at"),
        ),
        [
            {"name": "Cash", "code": "cash", "payment_type": "cash", "is_system": True,
             "requires_reference": False, "icon": "banknote", "is_active": True,
             "created_at": now, "updated_at": now},
            {"name": "UPI", "code": "upi", "payment_type": "upi", "is_system": True,
             "requires_reference": True, "icon": "smartphone", "is_active": True,
             "created_at": now, "updated_at": now},
            {"name": "Credit Card", "code": "credit_card", "payment_type": "credit_card",
             "is_system": True, "requires_reference": True, "icon": "credit-card",
             "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Debit Card", "code": "debit_card", "payment_type": "debit_card",
             "is_system": True, "requires_reference": True, "icon": "credit-card",
             "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Net Banking", "code": "net_banking", "payment_type": "net_banking",
             "is_system": True, "requires_reference": True, "icon": "globe",
             "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Bank Transfer / NEFT / RTGS", "code": "bank_transfer",
             "payment_type": "bank_transfer", "is_system": True, "requires_reference": True,
             "icon": "building-2", "is_active": True, "created_at": now, "updated_at": now},
        ],
    )

    # ── Default currency (INR) ────────────────────────────────────────
    op.bulk_insert(
        sa.table(
            "currencies",
            sa.column("code"), sa.column("name"), sa.column("symbol"),
            sa.column("exchange_rate"), sa.column("decimal_places"), sa.column("is_default"),
            sa.column("is_active"), sa.column("created_at"), sa.column("updated_at"),
        ),
        [
            {"code": "INR", "name": "Indian Rupee", "symbol": "₹", "exchange_rate": 1.0,
             "decimal_places": 2, "is_default": True, "is_active": True,
             "created_at": now, "updated_at": now},
        ],
    )

    # ── System departments ────────────────────────────────────────────
    departments = [
        {"name": "Front Office / Reception", "code": "RECEPTION", "display_order": 1},
        {"name": "Restaurant & F&B", "code": "RESTAURANT", "display_order": 2},
        {"name": "Kitchen", "code": "KITCHEN", "display_order": 3},
        {"name": "Housekeeping", "code": "HOUSEKEEPING", "display_order": 4},
        {"name": "Maintenance", "code": "MAINTENANCE", "display_order": 5},
        {"name": "Accounts & Finance", "code": "ACCOUNTS", "display_order": 6},
        {"name": "Management", "code": "MANAGEMENT", "display_order": 7},
    ]
    op.bulk_insert(
        sa.table(
            "departments",
            sa.column("name"), sa.column("code"), sa.column("is_system"),
            sa.column("display_order"), sa.column("is_active"),
            sa.column("created_at"), sa.column("updated_at"),
        ),
        [
            {**d, "is_system": True, "is_active": True,
             "created_at": now, "updated_at": now}
            for d in departments
        ],
    )

    # ── System guest ID types ─────────────────────────────────────────
    op.bulk_insert(
        sa.table(
            "guest_id_types",
            sa.column("name"), sa.column("code"), sa.column("description"),
            sa.column("is_system"), sa.column("requires_expiry"), sa.column("display_order"),
            sa.column("is_active"), sa.column("created_at"), sa.column("updated_at"),
        ),
        [
            {"name": "Aadhaar Card", "code": "AADHAAR", "description": "12-digit UIDAI Aadhaar",
             "is_system": True, "requires_expiry": False, "display_order": 1,
             "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Passport", "code": "PASSPORT", "description": "International passport",
             "is_system": True, "requires_expiry": True, "display_order": 2,
             "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Driving Licence", "code": "DL", "description": "Motor driving licence",
             "is_system": True, "requires_expiry": True, "display_order": 3,
             "is_active": True, "created_at": now, "updated_at": now},
            {"name": "PAN Card", "code": "PAN", "description": "Income Tax PAN",
             "is_system": True, "requires_expiry": False, "display_order": 4,
             "is_active": True, "created_at": now, "updated_at": now},
            {"name": "Voter ID / EPIC", "code": "VOTER_ID", "description": "Election ID card",
             "is_system": True, "requires_expiry": False, "display_order": 5,
             "is_active": True, "created_at": now, "updated_at": now},
        ],
    )

    # ── New permissions for property config module ────────────────────
    op.bulk_insert(
        sa.table(
            "permissions",
            sa.column("code"), sa.column("name"), sa.column("module"),
            sa.column("description"), sa.column("is_system"),
            sa.column("is_active"), sa.column("created_at"), sa.column("updated_at"),
        ),
        [
            {"code": "property:view", "name": "View Property Config",
             "module": "property", "description": "View all property configuration",
             "is_system": True, "is_active": True, "created_at": now, "updated_at": now},
            {"code": "property:create", "name": "Create Property Config",
             "module": "property", "description": "Create floors, rooms, room types etc.",
             "is_system": True, "is_active": True, "created_at": now, "updated_at": now},
            {"code": "property:update", "name": "Update Property Config",
             "module": "property", "description": "Update property configuration records",
             "is_system": True, "is_active": True, "created_at": now, "updated_at": now},
            {"code": "property:delete", "name": "Delete Property Config",
             "module": "property", "description": "Soft-delete property configuration records",
             "is_system": True, "is_active": True, "created_at": now, "updated_at": now},
            {"code": "restaurant:config:view", "name": "View Restaurant Config",
             "module": "restaurant", "description": "View restaurant menus and tables",
             "is_system": True, "is_active": True, "created_at": now, "updated_at": now},
            {"code": "restaurant:config:manage", "name": "Manage Restaurant Config",
             "module": "restaurant", "description": "Full CRUD on restaurant configuration",
             "is_system": True, "is_active": True, "created_at": now, "updated_at": now},
            {"code": "organization:view", "name": "View Organization Config",
             "module": "organization", "description": "View departments and designations",
             "is_system": True, "is_active": True, "created_at": now, "updated_at": now},
            {"code": "organization:manage", "name": "Manage Organization Config",
             "module": "organization", "description": "Manage departments, designations, guest ID types",
             "is_system": True, "is_active": True, "created_at": now, "updated_at": now},
            {"code": "settings:view", "name": "View Business Settings",
             "module": "settings", "description": "View business settings",
             "is_system": True, "is_active": True, "created_at": now, "updated_at": now},
            {"code": "settings:manage", "name": "Manage Business Settings",
             "module": "settings", "description": "Update business settings",
             "is_system": True, "is_active": True, "created_at": now, "updated_at": now},
        ],
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("menu_item_modifiers")
    op.drop_table("menu_modifier_options")
    op.drop_table("menu_modifiers")
    op.drop_table("menu_items")
    op.drop_table("kitchen_stations")
    op.drop_table("menu_categories")
    op.drop_table("restaurant_categories")
    op.drop_table("restaurant_tables")
    op.drop_table("rate_plan_season_rates")
    op.drop_table("rate_plans")
    op.drop_table("seasons")
    op.drop_table("currencies")
    op.drop_table("payment_methods")
    op.drop_table("taxes")
    op.drop_table("rooms")
    op.drop_table("room_type_amenities")
    op.drop_table("room_type_images")
    op.drop_table("room_types")
    op.drop_table("bed_types")
    op.drop_table("amenities")
    op.drop_table("floors")
    op.drop_table("property_profiles")
    op.drop_table("designations")
    op.drop_table("departments")
    op.drop_table("guest_id_types")
    op.drop_table("business_settings")
