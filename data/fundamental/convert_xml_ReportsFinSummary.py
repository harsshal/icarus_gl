from bs4 import BeautifulSoup
import pandas as pd
# Re-extract the data from the XML document and include all types of financial data
# Load the XML file
with open("C:/Users/starf/OneDrive/Desktop/icarus_gl/AAPL_ReportsFinSummary.xml", "r") as file:
    xml_content = file.read()

# Parse XML with BeautifulSoup
soup = BeautifulSoup(xml_content, 'xml')

# Find all FYActual tags within the XML
fy_actuals = soup.find_all('FYActual')

# Initialize a list to store the data
all_financial_data = []

# Find the root financial summary tag
financial_summary = soup.find('FinancialSummary')

# Loop through each child tag in the FinancialSummary
for tag in financial_summary.find_all(True):
    # Each tag can represent a different financial metric
    financial_type = tag.name
    for entry in tag.find_all(True):  # True ensures we get all child tags regardless of the tag name
        data_entry = {
            'Type': financial_type,
            'asofDate': entry.get('asofDate'),
            'period': entry.get('period'),
            'reportType': entry.get('reportType'),
            'value': entry.text.strip()
        }
        all_financial_data.append(data_entry)

# Convert the list to a DataFrame
complete_financial_df = pd.DataFrame(all_financial_data)

# Save the DataFrame to a new CSV file
complete_csv_file_path = 'C:/Users/starf/OneDrive/Desktop/icarus_gl/AAPL_ReportsFinSummary.csv'
complete_financial_df.to_csv(complete_csv_file_path, index=False)

complete_financial_df.head(), complete_csv_file_path
