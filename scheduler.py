import schedule
import time
import logging
from logging.handlers import TimedRotatingFileHandler
# OOP 
from data_pipeline import processing_data

# /home/phattie/Desktop/Sligro Assesment/sligro/logs/scheduler.log

## Logging file support to check the scheduler is running
logging.basicConfig(
    handlers=[TimedRotatingFileHandler(filename="/app/logs/scheduler.log", when="midnight", interval=1)],
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

schedule.every(30).minutes.do(processing_data)

while True:
    schedule.run_pending()
    logging.info("Scheduler is running...")
    time.sleep(20)