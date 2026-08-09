"""
Inventory widget service for NiralayOS Dashboard.

Queries real InventoryItem data from the database.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import InventoryAlert, InventoryWidget, KPIInventory


class InventoryService:
    """Business logic for the Inventory dashboard widget."""

    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = DashboardRepository(db)

    def get_widget(self) -> InventoryWidget:
        kpi = self.get_kpi()
        alerts = self.get_alerts()
        return InventoryWidget(kpi=kpi, alerts=alerts)

    def get_kpi(self) -> KPIInventory:
        # Query real inventory data
        try:
            from sqlalchemy import select, func as sqlfunc
            from app.models.inventory import InventoryItem

            stmt = select(InventoryItem).where(
                InventoryItem.is_active.is_(True),
                InventoryItem.minimum_stock > 0,
            )
            items = self._db.scalars(stmt).all()

            low = critical = ok = 0
            for item in items:
                level = item.stock_level
                if level == "critical":
                    critical += 1
                elif level == "low":
                    low += 1
                else:
                    ok += 1

            # Also count items with no minimum_stock (always ok)
            no_min_stmt = select(sqlfunc.count(InventoryItem.id)).where(
                InventoryItem.is_active.is_(True),
                InventoryItem.minimum_stock == 0,
            )
            ok += self._db.scalar(no_min_stmt) or 0

            return KPIInventory(
                low_stock_count=low,
                critical_count=critical,
                ok_count=ok,
            )
        except Exception:
            # Fallback if inventory tables don't exist yet (e.g. test environment)
            return KPIInventory(low_stock_count=0, critical_count=0, ok_count=0)

    def get_alerts(self, include_ok: bool = False) -> list[InventoryAlert]:
        """Return inventory items at or below minimum stock level."""
        try:
            from sqlalchemy import select
            from app.models.inventory import InventoryItem

            stmt = (
                select(InventoryItem)
                .where(
                    InventoryItem.is_active.is_(True),
                    InventoryItem.minimum_stock > 0,
                    InventoryItem.current_stock <= InventoryItem.minimum_stock,
                )
                .limit(20)
            )
            items = self._db.scalars(stmt).all()

            alerts: list[InventoryAlert] = []
            for item in items:
                level = item.stock_level
                if not include_ok and level == "ok":
                    continue
                alerts.append(
                    InventoryAlert(
                        id=item.id,
                        item_name=item.name,
                        current_quantity=float(item.current_stock),
                        unit=item.unit,
                        minimum_quantity=float(item.minimum_stock),
                        level=level,
                        category=item.category.name if item.category else None,
                    )
                )

            alerts.sort(key=lambda a: (0 if a.level == "critical" else 1, a.item_name))
            return alerts
        except Exception:
            return []
