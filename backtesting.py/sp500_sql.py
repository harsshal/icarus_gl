import pandas as pd
from sp500 import get_sp500_tickers  # Import the function from the file that fetches SP500 data
from save_sql import save_dataframe_to_mysql  # Import save function from the MySQL saving module

# Fetch the S&P 500 tickers and company names
df = get_sp500_tickers()

# Specify the MySQL database connection URL
db_url = 'mysql+pymysql://icarus-user:gl_icarus@localhost/interactive_data'

# Specify the table name where the DataFrame should be saved
table_name = 'sp500_tickers'

# Call the save function to save the DataFrame to MySQL
save_dataframe_to_mysql(df, db_url, table_name)

# Print the last few rows of the DataFrame for confirmation
print(df.tail(10))
