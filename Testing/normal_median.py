from flask import Flask, jsonify
import psycopg2
import statistics
from datetime import datetime
import os

# Load environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

app = Flask(__name__)

@app.route('/metrics/orders', methods=['GET'])


def get_metrics():
    connection = psycopg2.connect(user=DB_USER,
                                password=DB_PASSWORD,
                                host=DB_HOST,
                                port=DB_PORT,
                                database=DB_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT customer_id, event_type, timestamp
        FROM events
        WHERE customer_id IN (SELECT DISTINCT customer_id FROM events WHERE event_type = 'placed_order')
        ORDER BY customer_id, timestamp;
    """)

    customer_data = cursor.fetchall()

    create_table_result_statistic = '''CREATE TABLE IF NOT EXISTS result_statistic 
            (times_id SERIAL PRIMARY KEY,
        median_visit INTEGER, 
        median_session INTEGER)'''
    
    cursor.execute(create_table_result_statistic)

    durations = []
    event_counts = []
    current_customer = None
    first_timestamp = None
    order_timestamp = None
    event_count = 0

    for customer_id, event_type, timestamp in customer_data:
        if customer_id != current_customer:
            if order_timestamp is not None and first_timestamp is not None:
                duration = (order_timestamp - first_timestamp).total_seconds() / 60.0
                durations.append(duration)
                event_counts.append(event_count)
            
            current_customer = customer_id
            first_timestamp = timestamp if event_type != 'placed_order' else None
            order_timestamp = timestamp if event_type == 'placed_order' else None
            event_count = 1 if event_type != 'placed_order' else 0
        else:
            if event_type == 'placed_order':
                order_timestamp = timestamp
            else:
                event_count += 1
                if first_timestamp is None:
                    first_timestamp = timestamp

    if order_timestamp is not None and first_timestamp is not None:
        duration = (order_timestamp - first_timestamp).total_seconds() / 60.0
        durations.append(duration)
        if customer_data[-1][1] == 'placed_order':
            event_counts.append(event_count)

    median_visit = calculate_median(event_counts)
    median_session = calculate_median(durations)

    cursor.execute("INSERT INTO result_statistic (median_visit, median_session) VALUES (%s, %s)", (median_visit, median_session))

    connection.commit()

    connection.close()
    
    return jsonify({
        "median_visits_before_order": median_visit,
        "median_session_duration_minutes_before_order": median_session
    })

def calculate_median(number):
    sorted_number = sorted(number)
    count = len(sorted_number)

    middle_index = (count- 1) // 2
    
    if (count % 2):
        return sorted_number[middle_index]
    else:
        return (sorted_number[middle_index] + sorted_number[middle_index + 1])/2.0

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
