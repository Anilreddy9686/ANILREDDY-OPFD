"""
app.py — Online Payment Fraud Detection v3.1 (Fixed & Stable)
Developed by ANILREDDY
Stack: Flask · PyMySQL · ML · Secure Session Handling
"""

# ─────────────────────────────────────────────────────────────
# ✅ MySQL Fix (No mysqlclient needed)
# ─────────────────────────────────────────────────────────────
import pymysql
pymysql.install_as_MySQLdb()

# ─────────────────────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────────────────────
from flask import Flask, redirect, url_for, session
from config import Config

# Blueprints
from modules.db        import init_db, mysql
from modules.auth      import auth_bp
from modules.otp       import otp_bp
from modules.predict   import predict_bp
from modules.admin     import admin_bp
from modules.history   import history_bp
from modules.analytics import analytics_bp
from modules.alerts    import alerts_bp
from modules.export    import export_bp
from modules.search    import search_bp
from modules.heatmap   import heatmap_bp
from modules.receipt   import receipt_bp
from modules.users     import users_bp
from modules.settings  import settings_bp

# ─────────────────────────────────────────────────────────────
# App Initialization
# ─────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)

# ─────────────────────────────────────────────────────────────
# 🔒 Security Config (Improved)
# ─────────────────────────────────────────────────────────────
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # change to True in production (HTTPS)
)

# ─────────────────────────────────────────────────────────────
# 🔌 Register Blueprints (Safe loop)
# ─────────────────────────────────────────────────────────────
blueprints = [
    auth_bp, otp_bp, predict_bp, admin_bp, history_bp,
    analytics_bp, alerts_bp, export_bp, search_bp,
    heatmap_bp, receipt_bp, users_bp, settings_bp
]

for bp in blueprints:
    try:
        app.register_blueprint(bp)
    except Exception as e:
        print(f"❌ Error registering blueprint: {bp} -> {e}")

# ─────────────────────────────────────────────────────────────
# 🗄️ Initialize Database
# ─────────────────────────────────────────────────────────────
try:
    init_db(app)
    print("✅ Database initialized successfully")
except Exception as e:
    print("❌ Database connection failed:", str(e))

# ─────────────────────────────────────────────────────────────
# 🌐 Routes
# ─────────────────────────────────────────────────────────────
@app.route("/")
def index():
    try:
        if "user_id" in session:
            return redirect(url_for("predict.dashboard"))
        return redirect(url_for("auth.login"))
    except Exception as e:
        return f"❌ Routing Error: {str(e)}"

# ─────────────────────────────────────────────────────────────
# 🚀 Run Server
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting Fraud Detection System...")
    app.run(debug=True, host="0.0.0.0", port=5000)