# import json
import requests
import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
import time
from tqdm import tqdm
import orjson as json

# Load the environment variables in the .env file
load_dotenv()

# Function that processes the data from Json into the database
def processing_data():
    # Start timing the processing
    start_time = time.time()
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

    # Check if the table already exists
    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name='events')")
    exists = cur.fetchone()[0]

    # If it exists, print the current number of rows
    if exists:
        cur.execute("SELECT COUNT(*) FROM events")
        count = cur.fetchone()[0]
        print(f"Existing rows in the 'events' table before processing: {count}")

    # If it doesn't exist, create it
    if not exists:
        create_table_query = '''CREATE TABLE events (
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

    # Initialize a counter for the number of lines processed
    lines_processed = 0

    # for line in tqdm(response.iter_lines(), desc="Processing lines"):
    # Loop over each line in the response
    for line in tqdm(response.iter_lines(), desc="Processing lines"):
        # If the line is not empty
        if line:
            # If we've processed 12000 lines already, break the loop
            # if lines_processed >= 15000:
            #     break

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

            # Increment the counter for the number of lines processed
            lines_processed += 1

    # Sort the DataFrame by customer_id
    df = df.sort_values('customer_id')

# 10.000 rows ()
    # Loop through each record in the DataFrame
    for index, row in df.iterrows():
        # Check if this row already exists in the table
        cur.execute("SELECT COUNT(*) FROM events WHERE customer_id=%s AND event_type=%s AND timestamp=%s", tuple(row))
        if cur.fetchone()[0] > 0:
        # If it does, skip it the count is greater than 0
            continue

        # Build the insert query with %s is a placeholder for the values
        query = "INSERT INTO events (customer_id, event_type, timestamp) VALUES (%s, %s, %s)"
  
        # Execute the query
        try:
            cur.execute(query, tuple(row))
            print(f"Successfully inserted row {index + 1} into the database.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error occurred while inserting row {index + 1} into the database: {error}")
            continue
    
    # Calculate processing time
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total processing time: {total_time / 60} minutes") # 41.5 minutes
    # Query to count the total number of rows
    cur.execute("SELECT COUNT(*) FROM events")
    count = cur.fetchone()[0]

    # Print the total number of rows
    print(f"Total rows in the 'events' table: {count}")

    # Commit the transaction
    conn.commit()
    # Close the connection
    cur.close()
    conn.close()

if __name__ == "__main__":
# Run the function
    processing_data()
