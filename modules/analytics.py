"""modules/analytics.py"""
from flask import Blueprint, render_template, session
from modules.security import login_required
from modules.db import query

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/analytics")
@login_required
def analytics():
    uid      = session["user_id"]
    is_admin = session.get("role") == "admin"

    # ✅ SAFE WHERE CLAUSE
    if is_admin:
        where_clause = ""
        params = None
    else:
        where_clause = "WHERE user_id = %s"
        params = (uid,)

    # 🔥 FIXED: %%Y-%%m (escape % for PyMySQL)
    monthly = query(f"""
        SELECT DATE_FORMAT(created_at,'%%Y-%%m') AS month,
               COUNT(*) AS total,
               SUM(CASE WHEN LOWER(prediction)='fraud' THEN 1 ELSE 0 END) AS frauds,
               COALESCE(SUM(amount_inr),0) AS volume
        FROM transactions {where_clause}
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """, params)

    by_type = query(f"""
        SELECT type,
               COUNT(*) AS total,
               SUM(CASE WHEN LOWER(prediction)='fraud' THEN 1 ELSE 0 END) AS frauds,
               COALESCE(AVG(amount_inr),0) AS avg_amount
        FROM transactions {where_clause}
        GROUP BY type
    """, params)

    risk_dist = query(f"""
        SELECT CASE
            WHEN risk_score < 30 THEN 'Low (0-29)'
            WHEN risk_score < 60 THEN 'Medium (30-59)'
            WHEN risk_score < 80 THEN 'High (60-79)'
            ELSE 'Critical (80+)'
        END AS band,
        COUNT(*) AS cnt
        FROM transactions {where_clause}
        GROUP BY band
        ORDER BY MIN(risk_score)
    """, params)

    # Admin-only
    top_users = []
    if is_admin:
        top_users = query("""
            SELECT u.username,
                   COUNT(*) AS txns,
                   SUM(CASE WHEN LOWER(t.prediction)='fraud' THEN 1 ELSE 0 END) AS frauds,
                   COALESCE(SUM(t.amount_inr),0) AS volume
            FROM transactions t
            JOIN users u ON t.user_id = u.id
            GROUP BY u.username
            ORDER BY frauds DESC
            LIMIT 10
        """)

    return render_template(
        "analytics.html",
        monthly=monthly or [],
        by_type=by_type or [],
        risk_dist=risk_dist or [],
        top_users=top_users or [],
        is_admin=is_admin
    )