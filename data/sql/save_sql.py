import pandas as pd
from sqlalchemy import create_engine
import pymysql
from dotenv import load_dotenv
import os

def save_dataframe_to_mysql(df, db_url, table_name, if_exists='replace', index=True):
    """
    Parameters:
    - df: pandas DataFrame to be saved
    - db_url: the database connection URL (format: mysql+pymysql://user:password@host/dbname)
    - table_name: the name of the table where data should be saved
    - if_exists: what to do if the table exists ('replace', 'append', 'fail')
    - index: whether to include the DataFrame's index as a column in the SQL table
    """
    if df.empty:
        print("DataFrame is empty. No data to save.")
        return

    try:
        # Create a SQLAlchemy engine
        engine = create_engine(db_url)
        
        # Save the DataFrame to the SQL table
        df.to_sql(table_name, con=engine, if_exists=if_exists, index=index)
        print(f"DataFrame successfully saved to table '{table_name}' in MySQL.")
    except Exception as e:
        print(f"Failed to save DataFrame to MySQL: {e}")
