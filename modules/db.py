"""
modules/db.py
MySQL connection + auto-create all tables
Developed by ANILREDDY | 9686809509
"""

# ===========================
# IMPORTS
# ===========================
import os
import sqlite3
import traceback   # ✅ NEW (debug)
from flask import g
from flask_mysqldb import MySQL

mysql = MySQL()

# ===========================
# AUTO SWITCH
# ===========================
USE_SQLITE = os.environ.get("USE_SQLITE", "0") == "1"
SQLITE_DB = "opfd.db"

# ===========================
# MYSQL / SQLITE SWITCH
# ===========================
def get_cursor():
    if USE_SQLITE:
        return get_sqlite_conn().cursor()

    if "db_conn" not in g:
        try:
            g.db_conn = mysql.connection   # ✅ SAFE MYSQL
        except Exception as e:
            print("⚠️ MySQL failed → switching to SQLite:", e)
            return get_sqlite_conn().cursor()

    return g.db_conn.cursor()


def query(sql, args=()):
    if USE_SQLITE:
        return sqlite_query(sql, args)

    try:
        cur = get_cursor()
        cur.execute(sql, args)
        return cur.fetchall()
    except Exception as e:
        print("❌ MYSQL QUERY ERROR:", e)
        traceback.print_exc()
        return []


def query_one(sql, args=()):
    if USE_SQLITE:
        res = sqlite_query(sql, args)
        return res[0] if res else None

    try:
        cur = get_cursor()
        cur.execute(sql, args)
        return cur.fetchone()
    except Exception as e:
        print("❌ MYSQL QUERY_ONE ERROR:", e)
        traceback.print_exc()
        return None


def execute(sql, args=()):
    if USE_SQLITE:
        return sqlite_execute(sql, args)

    try:
        conn = mysql.connection
        cur  = conn.cursor()
        cur.execute(sql, args)
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print("❌ MYSQL EXEC ERROR:", e)
        traceback.print_exc()
        return None


# ===========================
# SQLITE CORE
# ===========================
def get_sqlite_conn():
    if "sqlite_db" not in g:
        g.sqlite_db = sqlite3.connect(SQLITE_DB, check_same_thread=False)  # ✅ FIX
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db


def sqlite_query(sql, args=()):
    conn = get_sqlite_conn()
    cur = conn.cursor()

    # Convert MySQL → SQLite
    sql = sql.replace("%s", "?")
    sql = sql.replace("AUTO_INCREMENT", "AUTOINCREMENT")
    sql = sql.replace("ENGINE=InnoDB", "")
    sql = sql.replace("DEFAULT CHARSET=utf8mb4", "")
    sql = sql.replace("ENUM('Fraud','Legitimate')", "TEXT")

    try:
        cur.execute(sql, args)
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print("❌ SQLITE QUERY ERROR:", e)
        print("SQL:", sql)
        traceback.print_exc()
        return []


def sqlite_execute(sql, args=()):
    conn = get_sqlite_conn()
    cur = conn.cursor()

    sql = sql.replace("%s", "?")

    try:
        cur.execute(sql, args)
        conn.commit()
        return cur.lastrowid
    except Exception as e:
        print("❌ SQLITE EXEC ERROR:", e)
        print("SQL:", sql)
        traceback.print_exc()
        return None


# ===========================
# SQLITE TABLE CREATION
# ===========================
def init_sqlite_tables():
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()

    # USERS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            password_hash TEXT,
            role TEXT DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 🔥 SAFE COLUMN ADD (NO CRASH)
    for col in [
        "is_active INTEGER DEFAULT 1",
        "login_attempts INTEGER DEFAULT 0",
        "locked_until DATETIME",
        "otp_enabled INTEGER DEFAULT 0",
        "email_verified INTEGER DEFAULT 0"
    ]:
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN {col}")
        except:
            pass

    # TRANSACTIONS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount_inr REAL,
            prediction TEXT,
            risk_score INTEGER,
            type TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # IP BLACKLIST
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ip_blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ALERTS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

    print("📊 SQLite tables initialized successfully")  # ✅ NEW


# ===========================
# INIT DB
# ===========================
def init_db(app):
    if USE_SQLITE:
        print("🟢 Using SQLite database")
        init_sqlite_tables()
        print("✅ SQLite DB ready")
        return

    mysql.init_app(app)

    with app.app_context():
        try:
            conn = mysql.connection
            cur  = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(60),
                    email VARCHAR(120),
                    password_hash VARCHAR(256),
                    role ENUM('user','admin') DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            print("✅ MySQL DB ready")

        except Exception as e:
            print("❌ MYSQL INIT ERROR:", e)
            traceback.print_exc()