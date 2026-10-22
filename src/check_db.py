"""
This file is the verification tool that pulls data directly from SQL
to the terminal so you can prove the Excel records were successfully saved.
"""

import pandas as pd

from models import engine

# This pulls everything from the work_logs table
df = pd.read_sql("SELECT * FROM work_logs", engine)

if df.empty:
    print("⚠️ The database is still empty!")
else:
    print("📊 Data found in SQL Table:")
    print(df)
