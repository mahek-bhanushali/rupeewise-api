from flask import Blueprint, g, jsonify, request

from ..auth_utils import token_required
from ..services.expense_service import ExpenseService, ValidationError

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.errorhandler(ValidationError)
def handle_validation_error(err):
    return jsonify({"error": str(err)}), 400


@expenses_bp.post("")
@token_required
def create_expense():
    expense = ExpenseService.create(g.current_user.id, request.get_json(silent=True))
    return jsonify(expense.to_dict()), 201


@expenses_bp.get("")
@token_required
def list_expenses():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 100)
    result = ExpenseService.list(
        g.current_user.id,
        category=request.args.get("category"),
        start=request.args.get("start"),
        end=request.args.get("end"),
        page=page,
        per_page=per_page,
    )
    return jsonify(
        {
            "items": [e.to_dict() for e in result.items],
            "page": result.page,
            "pages": result.pages,
            "total": result.total,
        }
    )


@expenses_bp.get("/summary")
@token_required
def summary():
    return jsonify(ExpenseService.summary(g.current_user.id))


@expenses_bp.get("/<int:expense_id>")
@token_required
def get_expense(expense_id):
    expense = ExpenseService.get(g.current_user.id, expense_id)
    if expense is None:
        return jsonify({"error": "Expense not found"}), 404
    return jsonify(expense.to_dict())


@expenses_bp.put("/<int:expense_id>")
@token_required
def update_expense(expense_id):
    expense = ExpenseService.get(g.current_user.id, expense_id)
    if expense is None:
        return jsonify({"error": "Expense not found"}), 404
    updated = ExpenseService.update(expense, request.get_json(silent=True))
    return jsonify(updated.to_dict())


@expenses_bp.delete("/<int:expense_id>")
@token_required
def delete_expense(expense_id):
    expense = ExpenseService.get(g.current_user.id, expense_id)
    if expense is None:
        return jsonify({"error": "Expense not found"}), 404
    ExpenseService.delete(expense)
    return "", 204
