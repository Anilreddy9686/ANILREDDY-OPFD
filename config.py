import os

class Config:
    # 🔐 Security
    SECRET_KEY = "opfd-anilreddy-secret-2025"
    PERMANENT_SESSION_LIFETIME = 1800  # 30 min

    # 🗄️ MySQL (UPDATED WITH YOUR CREDENTIALS)
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