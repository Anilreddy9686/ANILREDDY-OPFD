import os

class Config:
    # 🔐 Security
    SECRET_KEY = "opfd-anilreddy-secret-2025"
    PERMANENT_SESSION_LIFETIME = 1800  # 30 min

    # 🗄️ MySQL (LOCAL - KEEP AS IS)
    MYSQL_HOST = "localhost"
    MYSQL_USER = "admin"
    MYSQL_PASSWORD = "admin@123"
    MYSQL_DB = "opfd_india"
    MYSQL_CURSORCLASS = "DictCursor"

    # 🔒 Security Controls
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # 📱 App Info
    APP_NAME = "Online Payment Fraud Detection"
    DEVELOPER = "ANILREDDY"
    MOBILE = "9686809509"
    VERSION = "3.1.0"

    # ─────────────────────────────────────────────
    # 🔥 NEW: CLOUD DATABASE SUPPORT (ADDED)
    # ─────────────────────────────────────────────
    MYSQL_HOST = os.getenv("MYSQL_HOST", MYSQL_HOST)
    MYSQL_USER = os.getenv("MYSQL_USER", MYSQL_USER)
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", MYSQL_PASSWORD)
    MYSQL_DB = os.getenv("MYSQL_DB", MYSQL_DB)

    # Optional: Port support
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))