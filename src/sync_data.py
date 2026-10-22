"""
Acts as the bridge that reads manual Excel entries,
cleans the formatting, and saves them into the SQL database as permanent records.
"""

import argparse
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

from models import AuditLog, WorkLog, logger, session


def sync_excel_to_sql(file_path: str = "Work_Logger_Frontend.xlsx"):
    """
    Import Excel data from the specified path 
    and update the SQL database accordingly.
    """

    try:
        df = pd.read_excel("Work_Logger_Frontend.xlsx")

        # Log file was opened successfully
        logger.info(f"Opened Excel file: '{file_path}': {len(df)} rows detected")

        # Clean headers
        df.columns = df.columns.str.strip().str.lower()

        if "hours" not in df.columns:
            logger.error(f"❌ Error! Found columns: {df.columns.tolist()}")
            # Record failed audit log
            failed_audit = AuditLog(
                timestamp=datetime.datetime.now(timezone.utc).isoformat(),
                file_path=file_path,
                status="Failed",
                rows_processed=0
            )
            session.add(failed_audit)
            session.commit()
            return

        df_filled = df.dropna(subset=["hours"])

        # Clear existing logs to prevent duplicates
        session.query(WorkLog).delete()
        logger.info("🗑️ Cleared existing WorkLog table for a fresh sync.")

        for _, row in df_filled.iterrows():
            new_log = WorkLog(
                employee_id=int(row["id"]),
                hours=float(row["hours"]),
                date=str(row["date"]),
            )
            session.add(new_log)

        # Record successful audit log
        success_audit = AuditLog(
            timestamp=datetime.now(timezone.utc).isoformat(),
            file_path=file_path,
            status="Success",
            rows_processed=len(df_filled)
        )
        session.add(success_audit)

        session.commit()
        logger.info(f"🚀 Success! Synced {len(df_filled)} rows from '{file_path}' to SQL.")

    except Exception as e:
        # Add a catch-all for unexpected crashes
        logger.critical(f"🧨 Pipeline crashed! {e!s}")
        session.rollback()

        # Record failure audit log in a fresh transaction state
        try:
            error_audit = AuditLog(
                timestamp=datetime.now(timezone.utc).isoformat(),
                file_path=file_path,
                status="Failed",
                rows_processed=0
            )
            session.add(error_audit)
            session.commit()
        except (SQLAlchemyError, OSError) as audit_err:
            logger.error(f"Failed to write error audit log due to database or I/O error: {audit_err}")
        
        raise
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Sync employee work hours from an Excel " 
                    "frontend into the SQL database."
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default="Work_Logger_Frontend.xslx",
        help="Path to the Excel frontend file (default: Work_Logger_Frontend.xlsx)"
    )
    args = parser.parse_args()

    sync_excel_to_sql()
