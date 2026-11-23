"""Business logic for expenses, kept separate from the HTTP layer."""
from datetime import date

from sqlalchemy import func

from ..extensions import db
from ..models import Expense


class ValidationError(Exception):
    """Raised when client input is invalid."""


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Invalid date '{value}'. Use YYYY-MM-DD.")


def validate_payload(data: dict, partial: bool = False) -> dict:
    """Validate and normalise expense input. Returns cleaned fields."""
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")

    cleaned = {}

    if "title" in data or not partial:
        title = str(data.get("title", "")).strip()
        if not title or len(title) > 100:
            raise ValidationError("title is required (max 100 characters).")
        cleaned["title"] = title

    if "amount" in data or not partial:
        try:
            amount = float(data.get("amount"))
        except (TypeError, ValueError):
            raise ValidationError("amount must be a number.")
        if amount <= 0:
            raise ValidationError("amount must be greater than 0.")
        cleaned["amount"] = round(amount, 2)

    if "category" in data:
        category = str(data["category"]).strip().lower()
        if not category or len(category) > 50:
            raise ValidationError("category must be 1-50 characters.")
        cleaned["category"] = category

    if "date" in data:
        cleaned["expense_date"] = parse_date(data["date"])

    if "note" in data:
        note = data["note"]
        if note is not None and len(str(note)) > 255:
            raise ValidationError("note must be at most 255 characters.")
        cleaned["note"] = note

    return cleaned


class ExpenseService:
    @staticmethod
    def create(user_id: int, data: dict) -> Expense:
        fields = validate_payload(data)
        expense = Expense(user_id=user_id, **fields)
        db.session.add(expense)
        db.session.commit()
        return expense

    @staticmethod
    def get(user_id: int, expense_id: int):
        return Expense.query.filter_by(id=expense_id, user_id=user_id).first()

    @staticmethod
    def list(user_id: int, category=None, start=None, end=None, page=1, per_page=10):
        query = Expense.query.filter_by(user_id=user_id)
        if category:
            query = query.filter(Expense.category == category.strip().lower())
        if start:
            query = query.filter(Expense.expense_date >= parse_date(start))
        if end:
            query = query.filter(Expense.expense_date <= parse_date(end))

        query = query.order_by(Expense.expense_date.desc(), Expense.id.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def update(expense: Expense, data: dict) -> Expense:
        fields = validate_payload(data, partial=True)
        for key, value in fields.items():
            setattr(expense, key, value)
        db.session.commit()
        return expense

    @staticmethod
    def delete(expense: Expense) -> None:
        db.session.delete(expense)
        db.session.commit()

    @staticmethod
    def summary(user_id: int) -> dict:
        rows = (
            db.session.query(
                Expense.category,
                func.sum(Expense.amount),
                func.count(Expense.id),
            )
            .filter(Expense.user_id == user_id)
            .group_by(Expense.category)
            .all()
        )
        by_category = [
            {"category": c, "total": round(t, 2), "count": n} for c, t, n in rows
        ]
        return {
            "total": round(sum(r["total"] for r in by_category), 2),
            "count": sum(r["count"] for r in by_category),
            "by_category": by_category,
        }
