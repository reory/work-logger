# Acts as the bridge that reads manual Excel entries,
# cleans the formatting, and saves them into the SQL database as permanent records.

import pandas as pd
from models import logger, session, WorkLog


def sync_excel_to_sql():
    """Import Excel data and update the SQL database accordingly."""

    try:
        df = pd.read_excel("Work_Logger_Frontend.xlsx")

        # Log file was opened successfully
        logger.info(f"Opened Excel file: {len(df)} rows detected")

        # Clean headers
        df.columns = df.columns.str.strip().str.lower()

        if "hours" not in df.columns:
            logger.error(f"❌ Error! Found columns: {df.columns.tolist()}")
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

        session.commit()
        logger.info(f"🚀 Success! Synced {len(df_filled)} rows to SQL.")

    except Exception as e:
        # Add a catch-all for unexpected crashes
        logger.critical(f"🧨 Pipeline crashed! {str(e)}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    sync_excel_to_sql()
