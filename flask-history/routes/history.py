from flask import Blueprint, request, jsonify
from db import get_db

history_bp = Blueprint("history", __name__)

@history_bp.route("/balance/<int:user_id>", methods=["GET"])
def get_balance(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT SUM(CASE WHEN type='income' THEN amount ELSE -amount END) FROM transactions WHERE user_id=%s", (user_id,))
    balance = cur.fetchone()[0] or 0
    return jsonify({"balance": balance})

@history_bp.route("/income/<int:user_id>", methods=["GET"])
def get_income(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id=%s AND type='income'", (user_id,))
    total = cur.fetchone()[0] or 0
    return jsonify({"total_income": total})

@history_bp.route("/expenses/<int:user_id>", methods=["GET"])
def get_expenses(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id=%s AND type='expense'", (user_id,))
    total = cur.fetchone()[0] or 0
    return jsonify({"total_expenses": total})

@history_bp.route("/recent/<int:user_id>", methods=["GET"])
def get_recent(user_id):
    start = request.args.get("start_date")
    end = request.args.get("end_date")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT transaction_id, name, amount, date, type, emoji
        FROM transactions
        WHERE user_id=%s AND date BETWEEN %s AND %s
        ORDER BY date DESC
    """, (user_id, start, end))
    rows = cur.fetchall()
    return jsonify(rows)
