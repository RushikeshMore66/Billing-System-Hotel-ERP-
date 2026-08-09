"""
Billing service for NiralayOS.

Handles bill creation, item management, payment processing, and void workflows.
All financial calculations are server-side — never trust frontend totals.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.billing import Bill, BillItem, Payment
from app.repositories.billing import BillRepository, PaymentRepository
from app.schemas.billing import BillCreate, BillItemCreate, BillUpdate, PaymentCreate


def _generate_bill_number(db: Session) -> str:
    """Generate sequential bill number from BusinessSettings format."""
    from datetime import datetime, timezone
    from app.models.settings import BusinessSettings
    from sqlalchemy import select

    # Get or create settings
    settings = db.scalars(select(BusinessSettings)).first()
    now = datetime.now(timezone.utc)

    if settings:
        seq = settings.invoice_sequence_start
        # Increment sequence for next use
        settings.invoice_sequence_start += 1
        db.flush()
        fmt = settings.invoice_number_format
        bill_num = (
            fmt
            .replace("{YYYY}", str(now.year))
            .replace("{MM}", f"{now.month:02d}")
            .replace("{DD}", f"{now.day:02d}")
            .replace("{SEQ}", f"{seq:05d}")
        )
    else:
        # Fallback if no settings exist
        bill_num = f"INV-{now.year}-{now.month:02d}-{now.day:02d}-{now.microsecond}"

    return bill_num


def _compute_item_totals(item_data: BillItemCreate) -> dict:
    """Compute server-side totals for a bill line item."""
    qty = item_data.quantity
    unit_price = item_data.unit_price
    discount_pct = item_data.discount_pct
    tax_rate = item_data.tax_rate

    amount = (qty * unit_price * (1 - discount_pct / 100)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    tax_amount = (amount * tax_rate / 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    total = amount + tax_amount

    return {
        "amount": amount,
        "tax_amount": tax_amount,
        "total": total,
    }


class BillingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = BillRepository(db)
        self.payment_repo = PaymentRepository(db)

    def get(self, bill_id: int) -> Bill:
        bill = self.repo.get_with_details(bill_id)
        if not bill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
        return bill

    def get_by_number(self, bill_number: str) -> Bill:
        bill = self.repo.get_by_number(bill_number)
        if not bill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bill not found")
        return bill

    def search(
        self,
        query: Optional[str] = None,
        status_filter: Optional[str] = None,
        bill_type: Optional[str] = None,
        reservation_id: Optional[int] = None,
        guest_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Bill], int]:
        return self.repo.search(
            query=query,
            status=status_filter,
            bill_type=bill_type,
            reservation_id=reservation_id,
            guest_id=guest_id,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
        )

    def create(self, data: BillCreate, current_user: Optional[str] = None) -> Bill:
        """
        Create a new bill with its line items.
        All financial totals are computed server-side.
        """
        bill_number = _generate_bill_number(self.db)

        bill = Bill(
            bill_number=bill_number,
            bill_date=data.bill_date or datetime.now(timezone.utc).date(),
            reservation_id=data.reservation_id,
            guest_id=data.guest_id,
            table_number=data.table_number,
            bill_type=data.bill_type,
            notes=data.notes,
            gst_number=data.gst_number,
            status="draft",
            subtotal=Decimal("0"),
            discount_amount=Decimal("0"),
            tax_amount=Decimal("0"),
            total_amount=Decimal("0"),
            amount_paid=Decimal("0"),
            amount_due=Decimal("0"),
            created_by=current_user,
        )
        self.db.add(bill)
        self.db.flush()

        # Add line items and compute totals
        self._recalculate_items(bill, data.items)

        self.db.flush()
        return bill

    def add_items(self, bill_id: int, items: list[BillItemCreate]) -> Bill:
        """Add line items to an existing draft bill."""
        bill = self.get(bill_id)
        if bill.status not in ("draft",):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot add items to a bill with status '{bill.status}'",
            )
        existing = list(bill.items)
        all_items_data = [
            BillItemCreate(
                item_type=i.item_type,
                description=i.description,
                quantity=i.quantity,
                unit_price=i.unit_price,
                discount_pct=i.discount_pct,
                tax_rate=i.tax_rate,
                display_order=i.display_order,
                notes=i.notes,
            )
            for i in existing
        ] + items
        self._recalculate_items(bill, all_items_data)
        self.db.flush()
        return self.get(bill_id)

    def issue_bill(self, bill_id: int) -> Bill:
        """Move bill from draft to issued (ready for payment)."""
        bill = self.get(bill_id)
        if bill.status != "draft":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Bill is already '{bill.status}', cannot issue",
            )
        if not bill.items:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Cannot issue an empty bill",
            )
        bill.status = "issued"
        self.db.flush()
        return bill

    def record_payment(
        self,
        bill_id: int,
        data: PaymentCreate,
        received_by: Optional[str] = None,
    ) -> Payment:
        """Record a payment against a bill and update bill status."""
        bill = self.get(bill_id)
        if bill.status in ("void", "paid"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot add payment to a '{bill.status}' bill",
            )

        payment_amount = data.amount
        if payment_amount > bill.amount_due:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Payment amount {payment_amount} exceeds outstanding balance {bill.amount_due}"
                ),
            )

        payment = Payment(
            bill_id=bill_id,
            payment_method_id=data.payment_method_id,
            amount=payment_amount,
            payment_date=data.payment_date or datetime.now(timezone.utc).date(),
            status="success",
            reference_number=data.reference_number,
            transaction_id=data.transaction_id,
            payment_type=data.payment_type,
            notes=data.notes,
            is_refund=False,
            received_by=received_by,
        )
        self.db.add(payment)
        self.db.flush()

        # Update bill payment tracking
        bill.amount_paid = (bill.amount_paid + payment_amount).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        bill.amount_due = (bill.total_amount - bill.amount_paid).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        # Update bill status
        if bill.amount_due <= 0:
            bill.status = "paid"
            bill.amount_due = Decimal("0")
        else:
            bill.status = "partially_paid"

        self.db.flush()
        return payment

    def void_bill(self, bill_id: int, reason: str, voided_by: Optional[str] = None) -> Bill:
        """Void a bill. Paid bills cannot be voided (use refund)."""
        bill = self.get(bill_id)
        if bill.status in ("paid",):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Paid bills cannot be voided. Create a refund instead.",
            )
        if bill.status == "void":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bill is already void",
            )
        bill.status = "void"
        bill.void_reason = reason
        bill.voided_at = datetime.now(timezone.utc)
        bill.voided_by = voided_by
        bill.is_active = False
        self.db.flush()
        return bill

    def update(self, bill_id: int, data: BillUpdate) -> Bill:
        bill = self.get(bill_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(bill, key, value)
        self.db.flush()
        return bill

    # ── Internal ─────────────────────────────────────────────────────────────

    def _recalculate_items(self, bill: Bill, items_data: list[BillItemCreate]) -> None:
        """Replace all bill items with new computed set and update bill totals."""
        # Remove existing items
        for item in list(bill.items):
            self.db.delete(item)
        self.db.flush()

        subtotal = Decimal("0")
        total_tax = Decimal("0")
        total_discount = Decimal("0")

        new_items = []
        for i, item_data in enumerate(items_data):
            totals = _compute_item_totals(item_data)
            bill_item = BillItem(
                bill_id=bill.id,
                item_type=item_data.item_type,
                description=item_data.description,
                menu_item_id=item_data.menu_item_id,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
                discount_pct=item_data.discount_pct,
                tax_rate=item_data.tax_rate,
                amount=totals["amount"],
                tax_amount=totals["tax_amount"],
                total=totals["total"],
                display_order=item_data.display_order or i,
                notes=item_data.notes,
            )
            self.db.add(bill_item)
            subtotal += totals["amount"]
            total_tax += totals["tax_amount"]

        # Update bill header totals
        bill.subtotal = subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        bill.tax_amount = total_tax.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        bill.discount_amount = total_discount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        bill.total_amount = (subtotal + total_tax - total_discount).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        bill.amount_due = (bill.total_amount - bill.amount_paid).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
