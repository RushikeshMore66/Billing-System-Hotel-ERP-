"""
Restaurant configuration models for NiralayOS.

Covers:
    RestaurantCategory — top-level groupings (e.g. Food, Beverages)
    MenuCategory       — items groupings with parent (sub-category support)
    KitchenStation     — where items are prepared (Grill, Bar, Bakery …)
    MenuItem           — individual F&B product
    MenuModifier       — modifier groups (Spice Level, Ice Level …)
    MenuModifierOption — individual choices within a modifier group
    RestaurantTable    — physical seating positions
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import AuditMixin, Base


# ---------------------------------------------------------------------------
# Association table: menu_items ↔ menu_modifiers  (many-to-many)
# ---------------------------------------------------------------------------
menu_item_modifiers = Table(
    "menu_item_modifiers",
    Base.metadata,
    Column(
        "menu_item_id",
        Integer,
        ForeignKey("menu_items.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "menu_modifier_id",
        Integer,
        ForeignKey("menu_modifiers.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "linked_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)


# ---------------------------------------------------------------------------
# RestaurantCategory  (top-level, e.g. Food / Beverages / Desserts)
# ---------------------------------------------------------------------------
class RestaurantCategory(AuditMixin, Base):
    """Top-level restaurant grouping."""

    __tablename__ = "restaurant_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    color: Mapped[Optional[str]] = mapped_column(
        String(7),
        nullable=True,
        comment="Hex color for UI display, e.g. #FF5733",
    )
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    menu_categories: Mapped[list["MenuCategory"]] = relationship(
        "MenuCategory",
        back_populates="restaurant_category",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("name", name="uq_restaurant_categories_name"),
        Index("ix_restaurant_categories_display_order", "display_order"),
    )


# ---------------------------------------------------------------------------
# MenuCategory  (hierarchical — parent_id enables sub-categories)
# ---------------------------------------------------------------------------
class MenuCategory(AuditMixin, Base):
    """
    Item grouping within a restaurant category.

    Supports one level of sub-categorisation via parent_id.
    """

    __tablename__ = "menu_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    restaurant_category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("restaurant_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("menu_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="NULL = top-level category; set = sub-category",
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Relationships
    restaurant_category: Mapped[Optional["RestaurantCategory"]] = relationship(
        "RestaurantCategory",
        back_populates="menu_categories",
    )
    parent: Mapped[Optional["MenuCategory"]] = relationship(
        "MenuCategory",
        remote_side="MenuCategory.id",
        back_populates="children",
        lazy="selectin",
    )
    children: Mapped[list["MenuCategory"]] = relationship(
        "MenuCategory",
        back_populates="parent",
        lazy="selectin",
    )
    menu_items: Mapped[list["MenuItem"]] = relationship(
        "MenuItem",
        back_populates="menu_category",
        lazy="dynamic",
    )

    __table_args__ = (
        Index("ix_menu_categories_display_order", "display_order"),
    )


# ---------------------------------------------------------------------------
# KitchenStation
# ---------------------------------------------------------------------------
class KitchenStation(AuditMixin, Base):
    """
    Area where specific menu items are prepared.

    Examples: Main Kitchen, Grill Station, Bar, Bakery, Cold Kitchen.
    """

    __tablename__ = "kitchen_stations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    printer_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="KOT printer name for this station",
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    menu_items: Mapped[list["MenuItem"]] = relationship(
        "MenuItem",
        back_populates="kitchen_station",
        lazy="dynamic",
    )

    __table_args__ = (
        UniqueConstraint("name", name="uq_kitchen_stations_name"),
    )


# ---------------------------------------------------------------------------
# MenuItem
# ---------------------------------------------------------------------------
class MenuItem(AuditMixin, Base):
    """Individual food & beverage product available for order."""

    __tablename__ = "menu_items"

    item_code: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        comment="Unique alphanumeric item code, e.g. BVR001",
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    menu_category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("menu_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    kitchen_station_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("kitchen_stations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    tax_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("taxes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Base selling price before tax",
    )
    cost_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Purchase/preparation cost for margin tracking",
    )
    food_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="veg",
        comment="veg | non_veg | vegan | jain | egg",
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        comment="Toggle availability without deleting",
    )
    prep_time_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Estimated preparation time in minutes",
    )
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    allergens: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Comma-separated allergen tags",
    )
    calories: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    menu_category: Mapped[Optional["MenuCategory"]] = relationship(
        "MenuCategory",
        back_populates="menu_items",
    )
    kitchen_station: Mapped[Optional["KitchenStation"]] = relationship(
        "KitchenStation",
        back_populates="menu_items",
    )
    modifiers: Mapped[list["MenuModifier"]] = relationship(
        "MenuModifier",
        secondary=menu_item_modifiers,
        back_populates="menu_items",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("item_code", name="uq_menu_items_item_code"),
        Index("ix_menu_items_food_type", "food_type"),
        Index("ix_menu_items_is_available", "is_available"),
    )


# ---------------------------------------------------------------------------
# MenuModifier
# ---------------------------------------------------------------------------
class MenuModifier(AuditMixin, Base):
    """
    A group of options that modify an item (e.g. Spice Level, Ice Level).

    Options within the group are stored in MenuModifierOption.
    """

    __tablename__ = "menu_modifiers"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    modifier_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="single",
        comment="single (radio) | multi (checkbox) | quantity",
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    min_selections: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_selections: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    options: Mapped[list["MenuModifierOption"]] = relationship(
        "MenuModifierOption",
        back_populates="modifier",
        cascade="all, delete-orphan",
        order_by="MenuModifierOption.display_order",
        lazy="selectin",
    )
    menu_items: Mapped[list["MenuItem"]] = relationship(
        "MenuItem",
        secondary=menu_item_modifiers,
        back_populates="modifiers",
        lazy="dynamic",
    )

    __table_args__ = (UniqueConstraint("name", name="uq_menu_modifiers_name"),)


# ---------------------------------------------------------------------------
# MenuModifierOption
# ---------------------------------------------------------------------------
class MenuModifierOption(Base):
    """Individual selectable choice within a modifier group."""

    __tablename__ = "menu_modifier_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    modifier_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("menu_modifiers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price_impact: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Amount added to (+) or subtracted from (-) base price",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    modifier: Mapped["MenuModifier"] = relationship("MenuModifier", back_populates="options")


# ---------------------------------------------------------------------------
# RestaurantTable
# ---------------------------------------------------------------------------
class RestaurantTable(AuditMixin, Base):
    """Physical seating position in the restaurant."""

    __tablename__ = "restaurant_tables"

    table_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Unique table identifier, e.g. T01, BAR-01",
    )
    capacity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=4,
        comment="Maximum number of guests",
    )
    section: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Named seating area, e.g. Terrace, Garden, VIP",
    )
    location_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="indoor",
        comment="indoor | outdoor | both",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="available",
        comment="available | occupied | reserved | cleaning | blocked",
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("table_number", name="uq_restaurant_tables_table_number"),
        Index("ix_restaurant_tables_status", "status"),
        Index("ix_restaurant_tables_section", "section"),
    )
