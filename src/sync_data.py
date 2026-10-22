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
        df = pd.read_excel(file_path)

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
        
        # Ensure hours is strictly numeric (prevents string/object comparison bugs)
        df_filled["hours"] = pd.to_numeric(df_filled["hours"], errors="coerce")
        df_filled = df_filled.dropna(subset=["hours"])

        # Statistical Anomaly Detection Validation
        # Flag and filter out extreme work-hour entries (> 12 hrs or negative hours)
        anomaly_threshold = 12.0
        anomalies = df_filled[(df_filled["hours"] > anomaly_threshold) | (df_filled["hours"] <0)]

        if not anomalies.empty:
            logger.warning(
                f"Anomaly Detected! Found {len(anomalies)} row(s) with exteme work hours "
                f"(> {anomaly_threshold} hours or negative). These entries will be filtered out."
            )
            for _, anom_row in anomalies.iterrows():
                logger.warning(
                    f" -> Employee ID: {anom_row.get('id', 'N/A')}, "
                    f"Hours Logged: {anom_row['hours']}, Date: {anom_row.get('date', 'N/A')}"
                )
        # Filter to keep only valid entries within normal parameters (0 - 12hrs)
        df_valid = df_filled[(df_filled["hours"] >= 0) & (df_filled["hours"] <= anomaly_threshold)]

        # Clear existing logs to prevent duplicates
        session.query(WorkLog).delete()
        logger.info("🗑️ Cleared existing WorkLog table for a fresh sync.")

        # Iterate over the clean valid verified rows that are comitted to the db
        for _, row in df_valid.iterrows():
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
            rows_processed=len(df_valid)
        )
        session.add(success_audit)

        session.commit()
        logger.info(
            f"🚀 Success! Synced {len(df_valid)} valid rows " 
            f"(filtered {len(anomalies)} anomalies) from '{file_path}' to SQL."
        )

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
        default="Work_Logger_Frontend.xlsx",
        help="Path to the Excel frontend file (default: Work_Logger_Frontend.xlsx)"
    )
    args = parser.parse_args()

    sync_excel_to_sql()
