import pandas as pd
from ibkr_data import get_ibkr_data  # Import the function from ibkr_data.py
from save_to_sql import save_dataframe_to_mysql  # Import save function

# Fetch historical data using the function from ibkr_data.py
df = get_ibkr_data('AAPL', '20240925 00:00:00', '1 D', '5 min')

# Specify the MySQL database connection URL
db_url = 'mysql+pymysql://icarus-user:gl_icarus@localhost/interactive_data'

# Specify the table name where data should be saved
table_name = 'historical_data'

# Call the save function to save the DataFrame to MySQL
save_dataframe_to_mysql(df, db_url, table_name)

# Print the last few rows of the DataFrame for confirmation
print(df.tail(10))
