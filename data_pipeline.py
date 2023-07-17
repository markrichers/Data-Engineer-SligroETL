import json
import requests
import pandas as pd
import psycopg2  # database 
from psycopg2.extras import execute_values
from tqdm import tqdm # progress bar - json check number
import os
from dotenv import load_dotenv

# Load the environment variables in the .env file
load_dotenv() # system environment variables /h
# Function that processes the data from Json into the database
def processing_data():
    # Load environment variables
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    print("Process run---")

    # Create a connection object to postgres
    conn = psycopg2.connect(user=DB_USER,
                                    password=DB_PASSWORD,
                                    host=DB_HOST,
                                    port=DB_PORT,
                                    database=DB_NAME)
    
    # Create a cursor object
    cur = conn.cursor()

    # Drop table if it exists
    drop_table_query = "DROP TABLE IF EXISTS events_number CASCADE;"
    cur.execute(drop_table_query)

    # Creating table
    create_table_query = '''CREATE TABLE events_number (
                            customer_id INTEGER,
                            event_type VARCHAR(255),
                            timestamp TIMESTAMP WITH TIME ZONE
                            ); '''
    cur.execute(create_table_query)

    # Define the URL
    url = 'https://storage.googleapis.com/xcc-de-assessment/events.json'

    # Send a HTTP request to the URL
    response = requests.get(url, stream=True)
    
    # Create an empty DataFrame to store the data
    df = pd.DataFrame(columns=['customer_id', 'event_type', 'timestamp'])

    # Loop over each line in the response
    for line in response.iter_lines():
        # If the DataFrame has reached the limit
        if len(df) >= 12000:
            break
        # If the line is not empty
        if line:
            # Parse the line as JSON
            event = json.loads(line)
            # Skip if customer_id is null
            if event['event']['customer-id'] is None:
                continue
            # Extract the fields and add them to the DataFrame
            df = df._append({
                'customer_id': event['event']['customer-id'], 
                'event_type': event['type'], 
                'timestamp': event['event']['timestamp']
            }, ignore_index=True)
    # Sort the DataFrame by customer_id
    df = df.sort_values('customer_id')

    # Loop through each record in the DataFrame
    for index, row in df.iterrows():
        # Build the insert query
        query = "INSERT INTO events_number (customer_id, event_type, timestamp) VALUES (%s, %s, %s)"
        # Execute the query
        try:
            cur.execute(query, tuple(row))
            print(f"Successfully inserted row {index + 1} into the database.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error occurred while inserting row {index + 1} into the database: {error}")
            continue

    # Commit the transaction
    conn.commit()
    # Close the connection
    cur.close()
    conn.close()

# # Initialize the object

if __name__ == "__main__":
    processing_data()