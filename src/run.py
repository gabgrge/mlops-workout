import multiprocessing
import schedule
import time

from app.app import *
from app.jobs import *


def start_flask_app():
    app.run(port=5001)


def start_scheduler():
    # Schedule the data pipeline stage to run every Monday at 00:00
    schedule.every().monday.at("00:00").do(data_pipeline_stage)

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
