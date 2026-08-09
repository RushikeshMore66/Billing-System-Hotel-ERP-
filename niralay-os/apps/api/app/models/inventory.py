"""
Inventory models for NiralayOS.

Covers the complete inventory management system:
    InventoryCategory, StoreLocation, InventoryItem, StockMovement

Design principles:
  - ONE generalised inventory system for all item types
    (food, kitchen equipment, linen, housekeeping supplies, etc.)
  - Stock is NEVER modified directly — all changes go through StockMovement
  - Every StockMovement is permanently recorded (never deleted)
  - Current stock is a derived field maintained via triggers in StockMovement
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base


# ---------------------------------------------------------------------------
# InventoryCategory
# ---------------------------------------------------------------------------
class InventoryCategory(AuditMixin, Base):
    """
    High-level grouping for inventory items.

    Examples: F&B, Kitchen Equipment, Linen, Housekeeping, Maintenance,
              Office Supplies, Crockery & Cutlery, Room Supplies.
    """

    __tablename__ = "inventory_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    color: Mapped[Optional[str]] = mapped_column(
        String(7),
        nullable=True,
        comment="Hex color for UI display, e.g. #155E4B",
    )
    icon: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Lucide icon name",
    )

    # Relationships
    items: Mapped[list["InventoryItem"]] = relationship(
        "InventoryItem",
        back_populates="category",
        lazy="dynamic",
    )

    __table_args__ = (
        UniqueConstraint("name", name="uq_inventory_categories_name"),
        Index("ix_inventory_categories_display_order", "display_order"),
    )


# ---------------------------------------------------------------------------
# StoreLocation
# ---------------------------------------------------------------------------
class StoreLocation(AuditMixin, Base):
    """
    Physical storage location within the property.

    Examples: Main Store, Kitchen Store, Housekeeping Store, Linen Store,
              Maintenance Store, Front Desk, Bar Store.
    """

    __tablename__ = "store_locations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    items: Mapped[list["InventoryItem"]] = relationship(
        "InventoryItem",
        back_populates="location",
        lazy="dynamic",
    )

    __table_args__ = (
        UniqueConstraint("code", name="uq_store_locations_code"),
        UniqueConstraint("name", name="uq_store_locations_name"),
    )


# ---------------------------------------------------------------------------
# InventoryItem
# ---------------------------------------------------------------------------
class InventoryItem(AuditMixin, Base):
    """
    A single inventory item master record.

    The current_stock field is the authoritative current quantity.
    It is updated atomically within each StockMovement transaction.

    item_type:
      consumable — used up on consumption (food, chemicals)
      reusable   — returned after use (linen, cutlery)
      asset      — long-lived equipment (TV, AC, refrigerator)
    """

    __tablename__ = "inventory_items"

    sku: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Stock-keeping unit — unique item identifier",
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("inventory_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    location_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("store_locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Measurement
    unit: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="piece",
        comment="piece | box | kg | gram | liter | bottle | pack | dozen | meter | set | custom",
    )
    item_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="consumable",
        comment="consumable | reusable | asset",
    )

    # Stock levels
    current_stock: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
        default=Decimal("0"),
        comment="Current stock quantity — updated on every StockMovement",
    )
    minimum_stock: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
        default=Decimal("0"),
        comment="Alert threshold — alerts fire when current_stock <= minimum_stock",
    )
    reorder_level: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 3),
        nullable=True,
        comment="Suggested reorder point (can differ from minimum_stock)",
    )
    maximum_stock: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 3),
        nullable=True,
        comment="Maximum storage capacity",
    )

    # Pricing
    purchase_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Last purchase price per unit",
    )

    # Media
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Supplier
    supplier_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    supplier_contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Expiry / Batch
    has_expiry: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    batch_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Tax
    tax_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(6, 2),
        nullable=True,
        comment="GST percentage applicable on purchase",
    )

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    category: Mapped[Optional["InventoryCategory"]] = relationship(
        "InventoryCategory",
        back_populates="items",
        lazy="joined",
    )
    location: Mapped[Optional["StoreLocation"]] = relationship(
        "StoreLocation",
        back_populates="items",
        lazy="joined",
    )
    movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="item",
        order_by="desc(StockMovement.movement_date)",
        lazy="dynamic",
    )

    @property
    def stock_level(self) -> str:
        """Classify stock level for alert purposes."""
        if self.minimum_stock and self.minimum_stock > 0:
            ratio = float(self.current_stock) / float(self.minimum_stock)
            if ratio <= 0.4:
                return "critical"
            if ratio <= 0.8:
                return "low"
        return "ok"

    __table_args__ = (
        UniqueConstraint("sku", name="uq_inventory_items_sku"),
        Index("ix_inventory_items_name", "name"),
        Index("ix_inventory_items_item_type", "item_type"),
        Index("ix_inventory_items_category_id", "category_id"),
    )


# ---------------------------------------------------------------------------
# StockMovement
# ---------------------------------------------------------------------------
class StockMovement(Base):
    """
    Immutable record of every stock change.

    Rules:
      - NEVER update or delete a StockMovement
      - quantity is always positive; direction is determined by movement_type
      - After insert, update InventoryItem.current_stock accordingly

    movement_type values and their effect on stock:
      opening     → +qty  (initial setup)
      purchase    → +qty  (goods received)
      return_in   → +qty  (item returned to store)
      consumption → -qty  (used in operations)
      damage      → -qty  (damaged/broken)
      loss        → -qty  (shrinkage/theft)
      adjustment  → ±qty  (manual correction — use signed quantity)
      transfer_in → +qty  (received from another location)
      transfer_out→ -qty  (sent to another location)
    """

    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("inventory_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    movement_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment=(
            "opening | purchase | return_in | consumption | damage | "
            "loss | adjustment | transfer_in | transfer_out"
        ),
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
        comment="Always positive for directional types; signed for adjustment",
    )
    stock_before: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
        comment="Stock quantity before this movement",
    )
    stock_after: Mapped[Decimal] = mapped_column(
        Numeric(12, 3),
        nullable=False,
        comment="Stock quantity after this movement",
    )
    unit_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Cost per unit for purchase movements",
    )
    total_cost: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # Reference info
    reference_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="e.g. purchase_order | consumption_log | manual",
    )
    reference_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="ID of the linked purchase order, bill, etc.",
    )
    supplier_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Transfer fields
    from_location_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("store_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    to_location_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("store_locations.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Audit
    movement_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
    )
    recorded_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    item: Mapped["InventoryItem"] = relationship("InventoryItem", back_populates="movements")
    from_location: Mapped[Optional["StoreLocation"]] = relationship(
        "StoreLocation",
        foreign_keys=[from_location_id],
        lazy="joined",
    )
    to_location: Mapped[Optional["StoreLocation"]] = relationship(
        "StoreLocation",
        foreign_keys=[to_location_id],
        lazy="joined",
    )

    __table_args__ = (
        Index("ix_stock_movements_item_id", "item_id"),
        Index("ix_stock_movements_movement_type", "movement_type"),
        Index("ix_stock_movements_movement_date", "movement_date"),
    )
