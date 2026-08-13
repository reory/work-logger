import runpy
import sys
from unittest.mock import patch

# Force Matplotlib to use a headless, non-GUI backend before importing pyplot
import matplotlib
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError

matplotlib.use("Agg")


def test_generate_summary_report_with_data():
    """Test generate_summary_report when DataFrame contains valid work log data."""
    
    if "src" not in sys.path:
        sys.path.insert(0, "src")

    # Sample non-empty dataset to trigger pivot_table and plotting code
    sample_data = pd.DataFrame([
        {"name": "Alice", "hours": 8, "date": "2026-08-10"},
        {"name": "Bob", "hours": 6, "date": "2026-08-10"},
        {"name": "Alice", "hours": 4, "date": "2026-08-11"}
    ])

    with patch("pandas.read_sql", return_value=sample_data) as mock_read_sql, \
         patch("matplotlib.pyplot.savefig") as mock_savefig, \
         patch("matplotlib.pyplot.close") as mock_close, \
         patch("builtins.print") as mock_print:
        
        from src.generate_report import generate_summary_report
        generate_summary_report()

        mock_read_sql.assert_called_once()
        mock_savefig.assert_called_once_with("work_report.png")
        mock_close.assert_called_once()
        mock_print.assert_called_with(
            "📅 Date-based graph generated! Check 'work_report.png'"
        )


def test_generate_summary_report_exception():
    """Test error handling when pd.read_sql raises a SQLAlchemyError."""

    if "src" not in sys.path:
        sys.path.insert(0, "src")

    with patch(
        "pandas.read_sql", 
        side_effect=SQLAlchemyError("Database connection failed")), \
         patch("builtins.print") as mock_print:
        
        from src.generate_report import generate_summary_report
        generate_summary_report()

        # Verify exception was caught and error message printed
        mock_print.assert_called_once()
        assert "❌ Failed to generate report" in mock_print.call_args[0][0]


def test_generate_report_main_block():
    """Test execution of line 71 (if __name__ == '__main__': block)."""

    if "src" not in sys.path:
        sys.path.insert(0, "src")

    sample_data = pd.DataFrame([{"name": "Alice", "hours": 8, "date": "2026-08-10"}])

    # Patch global functions so runpy can safely execute the script in __main__ mode
    with patch("pandas.read_sql", return_value=sample_data) as mock_read_sql, \
         patch("matplotlib.pyplot.savefig") as mock_savefig, \
         patch("matplotlib.pyplot.close"):
        
        runpy.run_path("src/generate_report.py", run_name="__main__")

        mock_read_sql.assert_called_once()
        mock_savefig.assert_called_once_with("work_report.png")