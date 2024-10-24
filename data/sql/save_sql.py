import pandas as pd
from sqlalchemy import create_engine, text
import pymysql
from dotenv import load_dotenv
import os

def save_dataframe_to_mysql(df, db_url, table_name, primary_keys, index=False):
    if df.empty:
        print("DataFrame is empty. No data to save.")
        return

    try:
        # Create a SQLAlchemy engine
        engine = create_engine(db_url)

        # Generate the ON DUPLICATE KEY UPDATE part dynamically, excluding primary keys
        update_columns = [col for col in df.columns if col not in primary_keys]
        update_stmt = ', '.join([f"{col} = VALUES({col})" for col in update_columns])

        # Connect to the database
        with engine.begin() as connection:
            # Loop over the DataFrame and insert/update row by row
            for index, row in df.iterrows():
                # Prepare an INSERT statement with ON DUPLICATE KEY UPDATE for MySQL
                insert_stmt = f"""
                INSERT INTO {table_name} 
                ({', '.join(df.columns)})
                VALUES ({', '.join([f':{col}' for col in df.columns])})
                ON DUPLICATE KEY UPDATE
                {update_stmt}
                """
                
                # Create a dictionary for the row data
                row_data = {col: row[col] for col in df.columns}

                # Print query and data for debugging
                #print(f"Executing query: {insert_stmt}")
                #print(f"With data: {row_data}")

                # Execute the statement
                connection.execute(text(insert_stmt), row_data)

        print(f"DataFrame successfully saved to table '{table_name}' with UPSERT in MySQL.")
    
    except Exception as e:
        print(f"Failed to save DataFrame to MySQL: {e}")
