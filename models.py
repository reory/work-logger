# Defines SQL database structure as Python classes, 
# ensuring data remains organized, consistent, and easy for other scripts to access.

import logging
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# Log the project pipeline
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(filename)s] - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WorkLogger")

Base = declarative_base()
engine = create_engine('sqlite:///work_logger.db')
Session = sessionmaker(bind=engine)
session = Session()

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    department = Column(String)

class WorkLog(Base):
    __tablename__ = "work_logs"
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    hours = Column(Float)
    date = Column(String)

# Create tables
Base.metadata.create_all(engine)
logger.info("Database models initialised and tables verified")