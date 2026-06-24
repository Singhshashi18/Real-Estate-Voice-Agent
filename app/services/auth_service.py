from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

from app.services.oauth_service import OAUTH_PLACEHOLDER_PASSWORD

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DB_PATH = settings.root_dir / "users.db"


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                auth_provider TEXT NOT NULL DEFAULT 'email',
                oauth_subject TEXT
            )
            """
        )
        columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(users)").fetchall()
        }
        if "auth_provider" not in columns:
            conn.execute(
                "ALTER TABLE users ADD COLUMN auth_provider TEXT NOT NULL DEFAULT 'email'"
            )
        if "oauth_subject" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN oauth_subject TEXT")
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_oauth
            ON users(auth_provider, oauth_subject)
            WHERE oauth_subject IS NOT NULL
            """
        )
        conn.commit()


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_user(name: str, email: str, password: str) -> dict:
    init_db()
    email = email.lower().strip()
    password_hash = hash_password(password)
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        with _get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (name.strip(), email, password_hash, created_at),
            )
            conn.commit()
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        raise ValueError("Email already registered") from exc

    return {"id": user_id, "name": name.strip(), "email": email}


def get_user_by_email(email: str) -> dict | None:
    init_db()
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, email, password_hash FROM users WHERE email = ?",
            (email.lower().strip(),),
        ).fetchone()
    if not row:
        return None
    return dict(row)


def get_user_by_id(user_id: int) -> dict | None:
    init_db()
    with _get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    if not row:
        return None
    return dict(row)


def authenticate_user(email: str, password: str) -> dict | None:
    user = get_user_by_email(email)
    if not user:
        return None
    if user.get("password_hash") == OAUTH_PLACEHOLDER_PASSWORD:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return {"id": user["id"], "name": user["name"], "email": user["email"]}


def get_user_by_oauth(provider: str, subject: str) -> dict | None:
    init_db()
    with _get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, name, email
            FROM users
            WHERE auth_provider = ? AND oauth_subject = ?
            """,
            (provider, subject),
        ).fetchone()
    if not row:
        return None
    return dict(row)


def get_or_create_oauth_user(
    provider: str, subject: str, email: str, name: str
) -> dict:
    init_db()
    email = email.lower().strip()
    name = name.strip() or email.split("@")[0]

    existing_oauth = get_user_by_oauth(provider, subject)
    if existing_oauth:
        return existing_oauth

    existing_email = get_user_by_email(email)
    if existing_email:
        with _get_connection() as conn:
            conn.execute(
                """
                UPDATE users
                SET auth_provider = ?, oauth_subject = ?, name = ?
                WHERE id = ?
                """,
                (provider, subject, name, existing_email["id"]),
            )
            conn.commit()
        return {
            "id": existing_email["id"],
            "name": name,
            "email": existing_email["email"],
        }

    created_at = datetime.now(timezone.utc).isoformat()
    with _get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (
                name, email, password_hash, created_at, auth_provider, oauth_subject
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                email,
                OAUTH_PLACEHOLDER_PASSWORD,
                created_at,
                provider,
                subject,
            ),
        )
        conn.commit()
        user_id = cursor.lastrowid

    return {"id": user_id, "name": name, "email": email}


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        user_id = int(payload.get("sub", 0))
        return user_id if user_id else None
    except (JWTError, ValueError):
        return None
