from flask import Flask, jsonify
import psycopg2
import statistics
from datetime import datetime
import os
import json
from psycopg2.extras import Json

# Load environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

app = Flask(__name__)

@app.route('/metrics/orders', methods=['GET'])
def get_metrics():
    connection = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )

    cursor = connection.cursor()

    # get all event data for customers who placed an order
    cursor.execute("""
        SELECT customer_id, event_type, timestamp
        FROM events
        WHERE customer_id IN (SELECT DISTINCT customer_id FROM events WHERE event_type = 'placed_order')
        ORDER BY customer_id, timestamp;
    """)

    customer_data = cursor.fetchall()

    # create the table

    create_table_result_statistic = '''CREATE TABLE IF NOT EXISTS result_statistic_test 
        (times_id SERIAL PRIMARY KEY,
    median_visit INTEGER, 
    median_session INTEGER,
    user_segmentation TEXT,
    median_products_viewed TEXT,
    user_path_analysis JSONB)''' 

    cursor.execute(create_table_result_statistic)

    # create a dictionary to store the frequency of each path
    path_frequency = {}

    # create variables to store data for current customer and the current path
    current_customer = None
    current_path = []

    for customer_id, event_type, timestamp in customer_data:
        if customer_id != current_customer:
            # new customer, finalize data for previous customer
            if current_customer is not None:
                path = tuple(current_path)
                path_frequency[path] = path_frequency.get(path, 0) + 1

            # reset data for new customer
            current_customer = customer_id
            current_path = []

        # add the event_type to the current path
        current_path.append(event_type)

    # finalize data for the last customer
    if current_customer is not None:
        path = tuple(current_path)
        path_frequency[path] = path_frequency.get(path, 0) + 1

    # sort the paths by frequency in descending order
    sorted_paths = sorted(path_frequency.items(), key=lambda x: x[1], reverse=True)

    # convert the paths to a list of dictionaries
    paths_list = [{"path": path, "frequency": frequency} for path, frequency in sorted_paths]

    # create empty lists to store data
    durations = []
    event_counts = []
    user_paths = {}  # Dictionary to store user paths

    # create variables to store data for current customer, timestamp of first event, timestamp of last event, and event count
    current_customer = None
    first_timestamp = None
    order_timestamp = None
    event_count = 0

    for customer_id, event_type, timestamp in customer_data:
        if customer_id != current_customer:
            # new customer, finalize data for previous customer
            if order_timestamp is not None and first_timestamp is not None:
                duration = (order_timestamp - first_timestamp).total_seconds() / 60.0
                durations.append(duration)
                event_counts.append(event_count)

                # Store user path for the customer
                user_paths[current_customer] = list(user_path)

            # reset data for new customer
            current_customer = customer_id
            user_path = []  # Initialize the user path
            first_timestamp = timestamp if event_type != 'placed_order' else None
            order_timestamp = timestamp if event_type == 'placed_order' else None
            event_count = 1 if event_type != 'placed_order' else 0
        else:
            # same customer, update data
            if event_type == 'placed_order':
                order_timestamp = timestamp
            else:
                event_count += 1
                if first_timestamp is None:
                    first_timestamp = timestamp

            # Append the event_type to the user path
            user_path.append(event_type)

    # finalize data for last customer with 60 minutes of data.
    if order_timestamp is not None and first_timestamp is not None:
        duration = (order_timestamp - first_timestamp).total_seconds() / 60.0
        durations.append(duration)
        if customer_data[-1][1] == 'placed_order':  # check if last event is 'placed_order'
            event_counts.append(event_count)

        # Store user path for the last customer
        user_paths[current_customer] = list(user_path)

    # calculate the median of the data
    median_visit = statistics.median(event_counts)
    median_session = statistics.median(durations)

    # calculate the median number of products viewed by each user
    median_products_viewed = calculate_median_products_viewed(customer_data)

 

    # Add the new column to the existing table if it doesn't exist
    # alter_table_query = '''
    #     ALTER TABLE result_statistic_test
    #     ADD COLUMN IF NOT EXISTS user_segmentation TEXT;
    # '''
    # cursor.execute(alter_table_query)

    # Add the new column to the existing table if it doesn't exist
    # alter_table_query2 = '''
    #     ALTER TABLE result_statistic_test
    #     ADD COLUMN IF NOT EXISTS median_products_viewed INTEGER;
    # '''
    # cursor.execute(alter_table_query2)

    # Insert the median, user path analysis, and user segmentation into the result_statistic table
    insert_query = '''
        INSERT INTO result_statistic_test (median_visit, median_session, user_segmentation, median_products_viewed, user_path_analysis)
        VALUES (%s, %s, %s, %s, %s);
    '''
    cursor.execute(
        insert_query,
        (median_visit, median_session, json.dumps(user_paths), calculate_user_segmentation(customer_data), Json(user_paths))
    )

    # commit the transaction
    connection.commit()

    # close the connection
    connection.close()

    return jsonify({
        "median_visits_before_order": median_visit,
        "median_session_duration_minutes_before_order": median_session,
        "user_segmentation": calculate_user_segmentation(customer_data),
        "median_products_viewed": median_products_viewed,
        "user_path_analysis": paths_list
    })

def calculate_user_segmentation(customer_data):
    # Implement your logic to calculate user segmentation
    # Example implementation: Return the most frequently occurring action event
    action_frequency = {}
    for _, event_type, _ in customer_data:
        if event_type != 'placed_order':
            action_frequency[event_type] = action_frequency.get(event_type, 0) + 1

    sorted_actions = sorted(action_frequency.items(), key=lambda x: x[1], reverse=True)
    if sorted_actions:
        most_frequent_action = sorted_actions[0][0]
        return most_frequent_action
    else:
        return None

def calculate_median_products_viewed(customer_data):
    products_viewed = {}
    for customer_id, event_type, _ in customer_data:
        if event_type == 'page_view':
            products_viewed[customer_id] = products_viewed.get(customer_id, 0) + 1

    num_products_viewed = list(products_viewed.values())
    if num_products_viewed:
        median_products_viewed = statistics.median(num_products_viewed)
        return median_products_viewed
    else:
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)