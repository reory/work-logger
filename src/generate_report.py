# Visualization engine that transforms raw SQL data
# into a professional bar chart to show work trends at a glance.

import pandas as pd
import matplotlib.pyplot as plt
from models import engine

def generate_summary_report():
    """Queries the database and generates a stacked bar chart of work hours."""
    try:
        # Pull the data including the Date
        query = (
            "SELECT e.name, w.hours, w.date "
            "FROM employees e JOIN work_logs w ON e.id = w.employee_id"
        )
        df = pd.read_sql(query, engine)

        # Handle empty data gracefully (stops pytest/empty database crashes)
        if df.empty:
            # Generate a simple empty placeholder image so the test file 
            # still generates
            plt.figure(figsize=(12, 7))
            plt.title(
                "Daily Hours Logged per Employee", 
                fontsize=16, fontweight="bold"
            )
            plt.text(
                0.5, 0.5, "No Work Logs Found Yet", 
                ha='center', va='center', fontsize=12
            )
            plt.savefig("work_report.png")
            plt.close()
            return

        # Pivot the data
        # This creates a table where Names are rows and Dates are columns
        pivot_df = df.pivot_table(
            index="name", columns="date", values="hours", aggfunc="sum"
        ).fillna(0)

        # Create the Stacked Bar Chart
        ax = pivot_df.plot(
            kind="bar", stacked=True, figsize=(12, 7), colormap="viridis"
        )
        
        # Formatting
        ax.set_title("Daily Hours Logged per Employee", fontsize=16, fontweight="bold")
        ax.set_xlabel("Employee Name", fontweight="bold")
        ax.set_ylabel("Total Hours", fontweight="bold")
        ax.legend(title="Date Worked", bbox_to_anchor=(1.05, 1), loc="upper left")
        ax.set_xticklabels(pivot_df.index, rotation=45)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        
        plt.tight_layout()

        # Save
        plt.savefig("work_report.png")
        plt.close()
        print("📅 Date-based graph generated! Check 'work_report.png'")

    except Exception as e:
        print(f"❌ Failed to generate report: {str(e)}")

# This ensures it ONLY runs when you execute the script directly, 
# not during test collection!
if __name__ == "__main__":
    generate_summary_report()
