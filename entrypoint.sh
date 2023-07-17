#!/bin/bash

# Run the data ingestion script
python data_pipeline.py

# After the data ingestion script completes, run the Flask API service
python flask_api.py
