"""
Generation & Initialization engine.
Uses the Faker library to seed the database with mock employees 
and exports the starter Work_Logger_Frontend.xlsx template.
"""

import argparse

import pandas as pd
from faker import Faker

from models import Base, Employee, engine, logger, session


def initialise_project(excel_path: str = "Work_Logger_Frontend.xlsx"):
    """Seed the database with mock employees and generate the Excel template."""

    fake = Faker()
    
    # Ensure the database tables are created
    Base.metadata.create_all(engine)
    
    # Check if db already have employees to avoid duplicate seeding
    existing_count = session.query(Employee).count()
    if existing_count > 0:
        logger.info(
            f"Database already seeded with {existing_count} employees. " 
            "Skipping seed."
        )
    else:
        logger.info("🌱 Seeding database with 50 fictional employees...")
        
        departments = [
            "Engineering", 
            "Marketing", 
            "Sales", 
            "HR", 
            "Finance", 
            "Operations"
        ]
        
        employees_to_add = []
        for _ in range(50):
            new_emp = Employee(
                name=fake.name(),
                department=fake.random_element(departments)
            )
            employees_to_add.append(new_emp)
            
        session.add_all(employees_to_add)
        session.commit()
        logger.info("✅ Successfully seeded 50 employees!")
    
    # Query all employees out of the DB to populate the Excel sheet template
    employees = session.query(Employee).all()
    data = {
        "ID": [emp.id for emp in employees],
        "Name": [emp.name for emp in employees],
        "Hours": ["" for _ in employees],  # Empty column for user input
        "Date": ["" for _ in employees]    # Empty column for user input
    }
    
    df = pd.DataFrame(data)
    df.to_excel(excel_path, index=False)
    logger.info(f"📁 Starter template generated successfully: '{excel_path}'")
    
    session.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialize project database and generate " 
                    "the starter Excel frontend template."
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default="Work_Logger_Frontend.xlsx",
        help="Path where the starter Excel template should be saved (default: Work_Logger_Frontend.xlsx)"
    )
    args = parser.parse_args()

    initialise_project(excel_path=args.file)