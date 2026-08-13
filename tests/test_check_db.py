import runpy
import sys
from unittest.mock import patch

import pandas as pd


def test_check_db_empty():
    """Test check_db.py when the SQL database has no records."""

    if "src" not in sys.path:
        sys.path.insert(0, "src")

    empty_df = pd.DataFrame()

    with patch("src.check_db.pd.read_sql", return_value=empty_df) as mock_read_sql, \
        patch("builtins.print") as mock_print:

        # Execute script
        runpy.run_path("src/check_db.py")

        # Assertions
        mock_read_sql.assert_called_once()
        mock_print.assert_called_once_with("⚠️ The database is still empty!")


def test_check_db_with_data():
    """Test check_db.py when the SQL database contains work log records."""

    if "src" not in  sys.path:
        sys.path.insert(0, "src")

    # Simulate database results
    sample_df = pd.DataFrame([{
        "id": 1, 
        "employee_id": 10, 
        "hours": 8, 
        "date": "2026-07-13"
    }])

    with patch("src.check_db.pd.read_sql", return_value=sample_df) as mock_read_sql, \
         patch("builtins.print") as mock_print:

        # Execute script
        runpy.run_path("src/check_db.py")

        # Assertions
        mock_read_sql.assert_called_once()

        assert mock_print.call_count >= 2