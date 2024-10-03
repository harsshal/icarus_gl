from sqlalchemy import create_engine
from get_price import *

def save_dataframe_to_sql(df, db_url, table_name):
    """
    Save a pandas DataFrame to an SQL table.

    Parameters:
    - df: pandas DataFrame to be saved
    - db_url: the database connection URL (e.g., mysql+pymysql://user:password@localhost/dbname)
    - table_name: the name of the table where data should be saved
    """
    # Create an SQLAlchemy engine
    engine = create_engine(db_url)
    
    # Save the DataFrame to a SQL table
    try:
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        print(f"Data saved to SQL table '{table_name}' successfully.")
    except Exception as e:
        print(f"Failed to save data to SQL table '{table_name}': {e}")

def main():
    # Specify the MySQL database connection URL and table name
    db_url = 'mysql+pymysql://icarus-user:gl_icarus@localhost/interactive_data'
    table_name = 'sp500_tickers'

    # Fetch tickers from SQL table
    tickers = get_tickers_from_sql(db_url, table_name)
    print(f"Tickers fetched from SQL: {tickers}")  # Debugging print

    # Fetch current prices and store them in a DataFrame
    price_df = fetch_current_prices(tickers)

    # Print the DataFrame
    print(price_df)

    save_dataframe_to_sql(price_df, db_url, 'current_price')


if __name__ == "__main__":
    main()
