import unittest
from flask.testing import FlaskClient

from .app import *
from .jobs import *

# Scheduler log file path
scheduler_log = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs/scheduler.log')

# Data Loading log file path
data_loading_log = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs/data_loading.log')


class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = FlaskClient(app, response_wrapper=app.response_class)

        # Clear the logs before each test
        open(data_loading_log, 'w').close()
        open(scheduler_log, 'w').close()

    def test_data_ingestion_job(self):
        # Run the data ingestion job
        data_ingestion_job()

        # Assert that the job completes successfully by checking the logs
        with open(scheduler_log, 'r') as log_file:
            log_contents = log_file.read()

            # Check that the log file contains the expected message
            self.assertIn("Data ingestion job complete.", log_contents)

    def test_workouts_endpoint(self):
        # Send a GET request to the /workouts endpoint
        response = self.client.get('/workouts')

        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Assert that the job completes successfully by checking the logs
        with open(data_loading_log, 'r') as log_file:
            log_contents = log_file.read()

            # Check that the log file contains the expected message
            self.assertIn("Workout data loaded.", log_contents)

    def test_my_exercises_endpoint(self):
        # Send a GET request to the /my-exercises endpoint
        response = self.client.get('/my-exercises')

        # Assert that the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Assert that the job completes successfully by checking the logs
        with open(data_loading_log, 'r') as log_file:
            log_contents = log_file.read()

            # Check that the log file contains the expected message
            self.assertIn("Filtered exercise data loaded.", log_contents)


if __name__ == '__main__':
    unittest.main()
