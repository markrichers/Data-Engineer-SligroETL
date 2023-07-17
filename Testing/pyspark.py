from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import os
from tqdm import tqdm
import requests
import orjson as json
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Start Spark Session
spark = SparkSession.builder \
    .appName("EventSessionsApp") \
    .getOrCreate()

# Define the URL
url = 'https://storage.googleapis.com/xcc-de-assessment/events.json'

# Send a HTTP request to the URL
response = requests.get(url, stream=True)

# Initialize an empty list to store the data
data = []

# Loop over each line in the response
for line in tqdm(response.iter_lines(), desc="Processing lines"):
    # If the line is not empty
    if line:
        # Parse the line as JSON
        event = json.loads(line)
        
        # Skip if customer_id is null
        if event['event']['customer-id'] is None:
            continue

        # Extract the fields and add them to the data list
        data.append((
            event['event']['customer-id'], 
            event['type'], 
            event['event']['timestamp']
        ))

# Define the schema
schema = StructType([
    StructField("customer_id", IntegerType(), False),
    StructField("event_type", StringType(), False),
    StructField("timestamp", TimestampType(), False),
])

# Convert the list into a DataFrame
df = spark.createDataFrame(data, schema)

# Define the database connection parameters
properties = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "driver": "org.postgresql.Driver"
}

# Define the JDBC url
url = f"jdbc:postgresql://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Read the existing data in the table
existing_df = spark.read.jdbc(url=url, table="event_sessions", properties=properties)

# Join the new data with the existing data to exclude duplicates
df = df.join(existing_df, on=["customer_id", "event_type", "timestamp"], how="left_anti")

# Write the DataFrame to a table in Postgres
df.write \
    .format("jdbc") \
    .option("url", f"jdbc:postgresql://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}") \
    .option("dbtable", "event_sessions") \
    .option("user", os.getenv('DB_USER')) \
    .option("password", os.getenv('DB_PASSWORD')) \
    .mode("append") \
    .save()

# Stop the Spark Session
spark.stop()
