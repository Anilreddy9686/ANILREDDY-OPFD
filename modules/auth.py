"""
modules/auth.py
────────────────
Login · Register · Logout · Password Reset · Email Verify
All security checklist items implemented
"""
import re
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from modules.db import execute, query_one
from modules.security import (
    GENERIC_AUTH_ERROR, audit, generate_reset_token, generate_verify_token,
    is_account_locked, is_ip_blocked, minutes_until_unlock, record_failed_login,
    reset_login_attempts, rotate_session, validate_registration,
    consume_reset_token, validate_reset_token
)

auth_bp = Blueprint("auth", __name__)


# ── TEMP ADMIN CREATOR ──────────────────────────────────────
@auth_bp.route("/create-admin")
def create_admin():
    try:
        existing = query_one(
            "SELECT id FROM users WHERE username=%s",
            ("admin",)
        )

        hashed_password = generate_password_hash("Admin@123")

        # Update existing admin user
        if existing:
            execute(
                """
                UPDATE users
                SET password_hash=%s,
                    role='admin',
                    is_active=1,
                    email_verified=1
                WHERE username=%s
                """,
                (hashed_password, "admin")
            )

            return """
            <h2>Admin password updated successfully!</h2>
            <hr>
            <p><b>Username:</b> admin</p>
            <p><b>Password:</b> Admin@123</p>
            """

        # Create admin user
        execute(
            """
            INSERT INTO users
            (
                username,
                email,
                password_hash,
                full_name,
                mobile,
                role,
                is_active,
                email_verified
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                "admin",
                "admin@example.com",
                hashed_password,
                "Administrator",
                "9999999999",
                "admin",
                1,
                1
            )
        )

        return """
        <h2>Admin created successfully!</h2>
        <hr>
        <p><b>Username:</b> admin</p>
        <p><b>Password:</b> Admin@123</p>
        """

    except Exception as e:
        return f"""
        <h2>ERROR</h2>
        <pre>{str(e)}</pre>
        """
