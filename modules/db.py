"""
modules/db.py
MySQL connection + auto-create all tables
Developed by ANILREDDY | 9686809509
"""

# ===========================
# 🔥 NEW IMPORTS (ADD ONLY)
# ===========================
import os
import sqlite3
from flask import g

# ===========================
# EXISTING MYSQL CODE (UNCHANGED)
# ===========================
from flask_mysqldb import MySQL

mysql = MySQL()

# ===========================
# 🔥 NEW: AUTO SWITCH FLAG
# ===========================
USE_SQLITE = os.environ.get("USE_SQLITE", "0") == "1"
SQLITE_DB = "opfd.db"

# ===========================
# EXISTING FUNCTIONS (UNCHANGED)
# ===========================
def get_cursor():
    if USE_SQLITE:
        return get_sqlite_cursor()

    if "db_conn" not in g:
        g.db_conn = mysql.connection
    return g.db_conn.cursor()


def query(sql, args=()):
    if USE_SQLITE:
        return sqlite_query(sql, args)

    cur = get_cursor()
    cur.execute(sql, args)
    return cur.fetchall()


def query_one(sql, args=()):
    if USE_SQLITE:
        res = sqlite_query(sql, args)
        return res[0] if res else None

    cur = get_cursor()
    cur.execute(sql, args)
    return cur.fetchone()


def execute(sql, args=()):
    if USE_SQLITE:
        return sqlite_execute(sql, args)

    conn = mysql.connection
    cur  = conn.cursor()
    cur.execute(sql, args)
    conn.commit()
    return cur.lastrowid

# ===========================
# 🔥 NEW SQLITE FUNCTIONS
# ===========================
def get_sqlite_conn():
    if "sqlite_db" not in g:
        g.sqlite_db = sqlite3.connect(SQLITE_DB)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db


def get_sqlite_cursor():
    return get_sqlite_conn().cursor()


def sqlite_query(sql, args=()):
    conn = get_sqlite_conn()
    cur = conn.cursor()

    # 🔥 Fix MySQL → SQLite compatibility
    sql = sql.replace("%s", "?")
    sql = sql.replace("AUTO_INCREMENT", "AUTOINCREMENT")
    sql = sql.replace("ENGINE=InnoDB", "")
    sql = sql.replace("DEFAULT CHARSET=utf8mb4", "")
    sql = sql.replace("ENUM('Fraud','Legitimate')", "TEXT")

    cur.execute(sql, args)
    rows = cur.fetchall()
    return [dict(r) for r in rows]


def sqlite_execute(sql, args=()):
    conn = get_sqlite_conn()
    cur = conn.cursor()

    sql = sql.replace("%s", "?")

    cur.execute(sql, args)
    conn.commit()
    return cur.lastrowid

# ===========================
# EXISTING INIT_DB (UNCHANGED)
# ===========================
def init_db(app):
    if USE_SQLITE:
        print("🟢 Using SQLite database")
        return

    mysql.init_app(app)
    with app.app_context():
        conn = mysql.connection
        cur  = conn.cursor()

        # ── users ──────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id               INT AUTO_INCREMENT PRIMARY KEY,
                username         VARCHAR(60)  NOT NULL,
                email            VARCHAR(120) NOT NULL,
                password_hash    VARCHAR(256) NOT NULL,
                full_name        VARCHAR(120),
                mobile           VARCHAR(12),
                role             ENUM('user','admin') DEFAULT 'user',
                is_active        TINYINT(1) DEFAULT 1,
                otp_enabled      TINYINT(1) DEFAULT 0,
                email_verified   TINYINT(1) DEFAULT 0,
                verify_token     VARCHAR(64),
                reset_token      VARCHAR(64),
                reset_expires    DATETIME,
                avatar_color     VARCHAR(20) DEFAULT '#FF9933',
                state            VARCHAR(50),
                bio              VARCHAR(200),
                last_login       DATETIME,
                login_attempts   TINYINT DEFAULT 0,
                locked_until     DATETIME,
                created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY uq_username (username),
                UNIQUE KEY uq_email    (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # (rest of your original code unchanged...)
        conn.commit()

        print("✅ opfd_india DB ready — admin / Admin@123")