import multiprocessing
import schedule
import time

from src.app.app import *
from src.app.jobs import *


def start_flask_app():
    app.run(port=5000)


def start_scheduler():
    # Schedule the job to run every Monday at 00:00
    schedule.every().monday.at("00:00").do(data_ingestion_job)

    # Temporarily schedule the job to run every 10 seconds for testing purposes
    schedule.every(20).seconds.do(data_ingestion_job)

    # Main loop to continuously check for scheduled jobs
    while True:
        schedule.run_pending()
        #time.sleep(60)  # Sleep for 60 seconds before checking again


if __name__ == '__main__':
    # Create processes
    flask_process = multiprocessing.Process(target=start_flask_app)
    scheduler_process = multiprocessing.Process(target=start_scheduler)

    # Start processes
    flask_process.start()
    scheduler_process.start()

    # Join processes
    flask_process.join()
    scheduler_process.join()
