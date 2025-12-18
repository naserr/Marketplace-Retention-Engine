"""Nightly retention engine that bridges SQL insights with marketing automation."""
from __future__ import annotations

import logging
import os
import sqlite3
from pathlib import Path
from typing import Iterable

import pandas as pd
from dotenv import load_dotenv

from connectors.braze_client import BrazeClient
from db_setup import initialize_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB_PATH = Path("marketplace.db")
SQL_PATH = Path("sql/churn_analysis.sql")
DEFAULT_CAMPAIGN_ID = "reactivation-journey-v1"


def ensure_database() -> None:
    """Create and seed the demo database if required."""
    if not DB_PATH.exists():
        logging.info("Database not found; bootstrapping demo data")
    initialize_database()


def load_query() -> str:
    """Load the churn analysis SQL from disk."""
    if not SQL_PATH.exists():
        raise FileNotFoundError(f"SQL file missing at {SQL_PATH}")
    return SQL_PATH.read_text(encoding="utf-8")


def run_segmentation(conn: sqlite3.Connection, query: str) -> pd.DataFrame:
    """Execute the churn analysis SQL and return at-risk users."""
    df = pd.read_sql_query(query, conn)
    return df


def trigger_reactivation(users: Iterable[pd.Series], client: BrazeClient, campaign_id: str) -> None:
    """Send each user to the mocked Braze campaign trigger."""
    for row in users:
        attributes = {
            "last_login_date": row.last_login_date,
            "ltv": row.total_spend,
            "segment": "at-risk-high-value",
        }
        success = client.trigger_campaign(user_id=int(row.user_id), campaign_id=campaign_id, attributes=attributes)
        if not success:
            logging.warning("Retryable failure for user %s", row.user_id)


def main() -> None:
    load_dotenv()
    ensure_database()

    campaign_id = os.getenv("BRAZE_CAMPAIGN_ID", DEFAULT_CAMPAIGN_ID)
    api_key = os.getenv("BRAZE_API_KEY")
    braze_client = BrazeClient(api_key=api_key)

    query = load_query()
    logging.info("Executing churn analysis SQL")
    with sqlite3.connect(DB_PATH) as conn:
        at_risk_df = run_segmentation(conn, query)

    user_count = len(at_risk_df)
    logging.info("Found %s at-risk users", user_count)
    if user_count == 0:
        logging.info("No users require re-activation tonight")
        return

    logging.info("Syncing with Braze...")
    trigger_reactivation(at_risk_df.itertuples(index=False), braze_client, campaign_id)
    logging.info("Finished enrolling users into campaign %s", campaign_id)


if __name__ == "__main__":
    main()
