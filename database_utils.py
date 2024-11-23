import os
import sqlite3
import pandas as pd

def insert_csv_to_db(db_file, csv_file):
    """
    Insert data from a CSV file into the SQLite database.

    Parameters:
    db_file (str): Path to the SQLite database file.
    csv_file (str): Path to the CSV file to be inserted.
    """
    try:
        # Check if the CSV file exists
        if not os.path.exists(csv_file):
            print(f"No CSV file found: {csv_file}")
            return
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_file)
        print(f"Loaded data from {csv_file}:\n{df.head()}")  # Preview data for debugging

        # Connect to SQLite database
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()

        # Insert data into the orders table
        for _, row in df.iterrows():
            try:
                cursor.execute("""
                INSERT INTO orders (
                    OrderNumber, StyleCode, Description, ColorCode, ColorName,
                    Quantity, Price, Total, Fabric, Composition,
                    SizeXS, SizeS, SizeM, SizeL, SizeXL, SizeXXL,
                    IssueDate, PickupDate, OwnershipDate, Season, Line
                )
                VALUES (
                    :OrderNumber, :StyleCode, :Description, :ColorCode, :ColorName,
                    :Quantity, :Price, :Total, :Fabric, :Composition,
                    :SizeXS, :SizeS, :SizeM, :SizeL, :SizeXL, :SizeXXL,
                    :IssueDate, :PickupDate, :OwnershipDate, :Season, :Line
                )
                ON CONFLICT(OrderNumber, StyleCode, ColorCode, Quantity)
                DO UPDATE SET
                    Price=excluded.Price,
                    Total=excluded.Total,
                    ColorName=excluded.ColorName,
                    Fabric=excluded.Fabric,
                    Season=excluded.Season;
                """, row.to_dict())
            except sqlite3.Error as e:
                print(f"Error inserting row: {row['OrderNumber']}, Error: {e}")
        
        # Commit the transaction
        connection.commit()
        print("Data inserted successfully.")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Close the connection
        if connection:
            connection.close()
