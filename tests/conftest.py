import os
import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

@pytest.fixture(scope="function")
def db_session():
    """Provides an isolated, in-memory SQLite database session for each test."""
    
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def mock_excel_file():
    """Creates a temporary Excel frontend file for testing, then deletes it."""

    file_path = "Work_Logger_Frontend.xlsx"
    
    # Create dummy data resembling the actual frontend template
    data = {
        "id": [1, 2],
        "name": [ "John Doe", "Jane Smith" ],
        "hours": [ 8.0, None ],
        "date": [ "2026-07-16", "" ]
    }
    
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    
    yield file_path
    
    # Cleanup after test ends
    if os.path.exists(file_path):
        os.remove(file_path)