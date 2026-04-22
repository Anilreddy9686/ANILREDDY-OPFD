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
# SQLITE CORE
# ===========================
def get_sqlite_conn():
    if "sqlite_db" not in g:
        g.sqlite_db = sqlite3.connect(SQLITE_DB)
        g.sqlite_db.row_factory = sqlite3.Row
    return g.sqlite_db


def sqlite_query(sql, args=()):
    conn = get_sqlite_conn()
    cur = conn.cursor()

    # Convert MySQL syntax → SQLite
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
# SQLITE TABLE CREATION (FIXED)
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

    # 🔥 FIXED ERROR TABLE
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
        conn = mysql.connection
        cur  = conn.cursor()

        # USERS TABLE
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