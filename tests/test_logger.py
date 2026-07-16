# tests/test_logger.py
import os
import pytest #noqa
from hypothesis import given, strategies as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import codebase modules
from models import Employee, WorkLog, Base
from sync_data import sync_excel_to_sql
from generate_report import generate_summary_report
from app import initialize_project

# Standard Employee Creation Test
def test_create_employee(db_session):
    """Test standard manual creation of an employee in the database."""

    emp = Employee(name="Alice Smith", department="Engineering")
    db_session.add(emp)
    db_session.commit()
    
    saved_emp = db_session.query(Employee).filter_by(name="Alice Smith").first()
    assert saved_emp is not None
    assert saved_emp.department == "Engineering"

# Hypothesis Stress Test (Property-based)
@given(
    hours=st.floats(
        min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False
    ),
    date_str=st.dates().map(str)
)
def test_work_log_property_types(hours, date_str):
    """Ensure WorkLog handles various valid hour ranges and dates."""

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        log = WorkLog(employee_id=1, hours=hours, date=date_str)
        session.add(log)
        session.commit()
        
        saved_log = session.query(WorkLog).first()
        assert saved_log is not None
        assert saved_log.hours == hours
        assert saved_log.date == date_str
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()

# Test sync_data.py pipeline
def test_sync_excel_to_sql(db_session, mock_excel_file):
    """Test that sync_data reads Excel rows, cleans, and saves to SQL."""

    # Run the importer function (it writes to the default database)
    sync_excel_to_sql()
    
    # Assertions on the global session used by sync_excel_to_sql
    from models import session as global_session
    try:
        logs = global_session.query(WorkLog).all()
        # Out of our 2 mock rows, only the 1 with hours should sync
        assert len(logs) == 1
        assert logs[0].employee_id == 1
        assert logs[0].hours == 8.0
    finally:
        # Clear out our test logs from the database
        global_session.query(WorkLog).delete()
        global_session.commit()

# Test generate_report.py engine
def test_generate_summary_report(db_session):
    """Test that report generator executes and outputs visual plot file."""

    report_file = "work_report.png"
    
    # Ensure any residual test files are gone
    if os.path.exists(report_file):
        os.remove(report_file)
        
    try:
        # Run generator (it runs fine even with an empty database)
        generate_summary_report()
        assert os.path.exists(report_file)
    finally:
        if os.path.exists(report_file):
            os.remove(report_file)

# Test app.py initialization
def test_initialize_project():
    """Test that app.py seeds employees and exports starter template."""

    excel_file = "Work_Logger_Frontend.xlsx"
    
    if os.path.exists(excel_file):
        os.remove(excel_file)
        
    try:
        initialize_project()
        assert os.path.exists(excel_file)
    finally:
        if os.path.exists(excel_file):
            os.remove(excel_file)