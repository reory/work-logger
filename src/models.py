"""
Defines SQL database structure as Python classes,
ensuring data remains organized, consistent, and easy for other scripts to access.
"""

import logging
import os

from dotenv import load_dotenv
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Log the project pipeline
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("WorkLogger")

Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite://worklogger.db")
engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()


class Employee(Base):
    """SQLAlchemy model representing an employee record in the database."""

    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    department = Column(String)


class WorkLog(Base):
    """SQLAlchemy model representing an individual work log entry."""
    
    __tablename__ = "work_logs"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    hours = Column(Float)
    date = Column(String)


# Create tables
Base.metadata.create_all(engine)
logger.info("Database models initialised and tables verified")
