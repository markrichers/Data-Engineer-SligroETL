# # Use an official Python runtime as a parent image
# FROM python:3.9

# # Set the working directory in the container to /app
# WORKDIR /app

# # Add the current directory contents into the container at /app
# ADD . /app

# RUN apt-get update && apt-get install -y wget ca-certificates
# RUN apt-get install -y --no-install-recommends postgresql
# RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
# # Install any needed packages specified in requirements.txt
# # Install pip

# # Create a directory for the logs
# RUN mkdir -p /app/logs

# # Install any needed packages specified in requirements.txt
# RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# # Make port 5000 available to the world outside this container
# EXPOSE 5000

# COPY . .

# RUN chmod +x /app/entrypoint.sh 

# # Run entrypoint.sh when the container launches
# ENTRYPOINT ["/app/entrypoint.sh"]

# # possiple to use like Cron job for every 10 minutes on the pipeline. 



# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

RUN apt-get update && apt-get install -y wget ca-certificates
RUN apt-get install -y --no-install-recommends postgresql
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

# Install any needed packages specified in requirements.txt
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Create a directory for the logs
RUN mkdir -p /app/logs

COPY . .

# Grant executable permissions to the entrypoint script
RUN chmod +x /app/entrypoint.sh 

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run entrypoint.sh when the container launches
ENTRYPOINT ["/app/entrypoint.sh"]
