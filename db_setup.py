"""Utility script to create and seed the demo SQLite database."""
from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB_PATH = Path("marketplace.db")


def _seed_data(now: datetime) -> Iterable[Tuple[str, str, float, str]]:
    """Construct seed rows with varied recency and spend profiles."""
    profiles = [
        ("alice@example.com", 10, 220.50, "active"),
        ("bob@example.com", 35, 120.00, "churned"),
        ("carol@example.com", 45, 55.25, "churned"),
        ("dave@example.com", 5, 15.00, "active"),
        ("erin@example.com", 75, 310.00, "churned"),
        ("frank@example.com", 25, 48.00, "active"),
        ("grace@example.com", 120, 540.10, "churned"),
        ("heidi@example.com", 32, 51.00, "churned"),
        ("ivan@example.com", 2, 5.00, "active"),
        ("judy@example.com", 90, 88.50, "churned"),
    ]

    for email, days_ago, spend, status in profiles:
        last_login = now - timedelta(days=days_ago)
        yield email, last_login.isoformat(), spend, status


def initialize_database() -> None:
    """Create the users table and seed demo records if empty."""
    logging.info("Ensuring SQLite database at %s", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                last_login TEXT NOT NULL,
                total_spend REAL NOT NULL DEFAULT 0,
                status TEXT NOT NULL
            );
            """
        )

        cursor.execute("SELECT COUNT(*) FROM users;")
        (existing_count,) = cursor.fetchone()
        if existing_count:
            logging.info("Database already seeded (%s users)", existing_count)
            return

        now = datetime.utcnow()
        cursor.executemany(
            "INSERT INTO users (email, last_login, total_spend, status) VALUES (?, ?, ?, ?);",
            list(_seed_data(now)),
        )
        conn.commit()
        logging.info("Seeded demo data into users table")
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_database()
