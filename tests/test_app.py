import runpy
import sys
from unittest.mock import MagicMock, patch


@patch("src.app.pd.DataFrame.to_excel")
@patch("src.app.session")
@patch("src.app.Base.metadata.create_all")
def test_initialise_project_seeding_path(mock_create_all, mock_session, mock_to_excel):
    """Test initialise_project when the database has 0 employees."""

    mock_query = MagicMock()
    mock_session.query.return_value = mock_query

    
    mock_query.count.return_value = 0

    # Simulate return value for session.query(Employee).all() after seeding
    mock_emp1 = MagicMock(id=1, name="Alice")
    mock_emp2 = MagicMock(id=2, name="Bob")
    mock_query.all.return_value = [mock_emp1, mock_emp2]

    # Import and execute function
    from src.app import initialise_project
    initialise_project()

    # Assertions
    mock_create_all.assert_called_once()
    mock_session.add_all.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_to_excel.assert_called_once_with("Work_Logger_Frontend.xlsx", index=False)
    mock_session.close.assert_called_once()


@patch("src.app.pd.DataFrame.to_excel")
@patch("src.app.session")
@patch("src.app.Base.metadata.create_all")
def test_app_main_block(mock_create_all, mock_session, mock_to_excel):
    """Test execution of line 71 (if __name__ == '__main__': block)."""
    
    if "src" not in sys.path:
        sys.path.insert(0, "src")

    # Set up basic mock returns to let initialise_project run cleanly
    mock_session.query.return_value.count.return_value = 1
    mock_session.query.return_value.all.return_value = []

    # Execute src/app.py as __main__
    runpy.run_path("src/app.py", run_name="__main__")

    # Verify side-effects triggered inside initialise_project()
    mock_create_all.assert_called_once()
    mock_to_excel.assert_called_once()