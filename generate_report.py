# Visualization engine that transforms raw SQL data 
# into a professional bar chart to show work trends at a glance.

import pandas as pd
import matplotlib.pyplot as plt
from models import engine

# Pull the data including the Date
query = "SELECT e.name, w.hours, w.date " \
        "FROM employees e JOIN work_logs w ON e.id = w.employee_id"
df = pd.read_sql(query, engine)

# Pivot the data
# This creates a table where Names are rows and Dates are columns
pivot_df = df.pivot_table(index='name', columns='date', values='hours', 
                          aggfunc='sum').fillna(0)

# Create the Stacked Bar Chart
ax = pivot_df.plot(kind='bar', stacked=True, figsize=(12, 7), colormap='viridis')

# Formatting
plt.title('Daily Hours Logged per Employee', fontsize=16, fontweight='bold')
plt.xlabel('Employee Name', fontweight='bold')
plt.ylabel('Total Hours', fontweight='bold')
plt.legend(title="Date Worked", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle=':', alpha=0.6)
plt.tight_layout()

# Save and Show
plt.savefig('work_report.png')
plt.show()

print("📅 Date-based graph generated! Check 'work_report.png'")