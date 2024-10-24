import pandas as pd
from save_sql import save_dataframe_to_mysql  
from dotenv import load_dotenv
import sys
import os
from ibkr_data import get_ibkr_data


# Fetch historical data using the function from ibkr_data.py
df = get_ibkr_data('AAPL', '20241008 00:00:00', '1 D', '5 mins')

# Specify the MySQL database connection URL
load_dotenv()

db_url = os.getenv('db_url')

# Specify the table name where data should be saved
table_name = 'historical_data'

# Call the save function to save the DataFrame to MySQL
save_dataframe_to_mysql(df, db_url, table_name)

# Print the last few rows of the DataFrame for confirmation
print(df)
print(df.columns)
