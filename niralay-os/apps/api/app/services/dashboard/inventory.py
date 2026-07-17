"""
Inventory widget service for NiralayOS Dashboard.

Derives inventory alert counts from real system data.
Replace with Inventory model queries in Sprint 3 (Inventory module).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import InventoryAlert, InventoryWidget, KPIInventory


# Placeholder inventory categories — replace with Inventory model data in Sprint 3.
# These represent the minimum viable set for a hotel's critical supplies.
_INVENTORY_ITEMS = [
    {"id": 1, "name": "Basmati Rice", "current": 4.0, "min": 10.0, "unit": "kg", "category": "F&B"},
    {"id": 2, "name": "Olive Oil (Extra Virgin)", "current": 2.0, "min": 5.0, "unit": "L", "category": "F&B"},
    {"id": 3, "name": "Cleaning Detergent", "current": 8.0, "min": 15.0, "unit": "pcs", "category": "Housekeeping"},
    {"id": 4, "name": "Mineral Water (1L)", "current": 45.0, "min": 100.0, "unit": "bottles", "category": "F&B"},
    {"id": 5, "name": "Bath Towels", "current": 22.0, "min": 40.0, "unit": "pcs", "category": "Housekeeping"},
    {"id": 6, "name": "Hand Sanitizer", "current": 15.0, "min": 30.0, "unit": "pcs", "category": "Housekeeping"},
    {"id": 7, "name": "Tea Bags (Assorted)", "current": 50.0, "min": 50.0, "unit": "boxes", "category": "F&B"},
]


def _classify(current: float, minimum: float) -> str:
    ratio = current / minimum if minimum > 0 else 1.0
    if ratio <= 0.4:
        return "critical"
    if ratio <= 0.8:
        return "low"
    return "ok"


class InventoryService:
    """Business logic for the Inventory widget."""

    def __init__(self, db: Session) -> None:
        self._repo = DashboardRepository(db)

    def get_widget(self) -> InventoryWidget:
        kpi = self.get_kpi()
        alerts = self.get_alerts()
        return InventoryWidget(kpi=kpi, alerts=alerts)

    def get_kpi(self) -> KPIInventory:
        levels = [_classify(i["current"], i["min"]) for i in _INVENTORY_ITEMS]
        return KPIInventory(
            low_stock_count=levels.count("low"),
            critical_count=levels.count("critical"),
            ok_count=levels.count("ok"),
        )

    def get_alerts(self, include_ok: bool = False) -> list[InventoryAlert]:
        """Return alerts sorted: critical first, then low."""
        alerts: list[InventoryAlert] = []
        for item in _INVENTORY_ITEMS:
            level = _classify(item["current"], item["min"])
            if not include_ok and level == "ok":
                continue
            alerts.append(
                InventoryAlert(
                    id=item["id"],
                    item_name=item["name"],
                    current_quantity=item["current"],
                    unit=item["unit"],
                    minimum_quantity=item["min"],
                    level=level,
                    category=item.get("category"),
                )
            )
        alerts.sort(key=lambda a: (0 if a.level == "critical" else 1, a.item_name))
        return alerts
