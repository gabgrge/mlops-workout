import unittest
from flask.testing import FlaskClient

from .app import *
from .jobs import *

# Scheduler log file path
scheduler_log = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs/scheduler.log')

# Data Loading log file path
data_loading_log = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs/data_loading.log')

# Model Training log file path
models_training_log = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs/models_training.log')

# Data Collection log file path
data_collection_log = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs/data_collection.log')


class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = FlaskClient(app, response_wrapper=app.response_class)

        # Save the logs to memory
        with open(data_loading_log, 'r') as f:
            self.data_loading_log_content = f.read()
        with open(scheduler_log, 'r') as f:
            self.scheduler_log_content = f.read()
        with open(data_collection_log, 'r') as f:
            self.data_collection_log_content = f.read()
        with open(models_training_log, 'r') as f:
            self.models_training_log_content = f.read()

        # Clear the logs used in the tests
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

    def test_model_training_job(self):
        # Run the model training job
        model_training_job(max_models=2)

        # Assert that the job completes successfully by checking the logs
        with open(scheduler_log, 'r') as log_file:
            log_contents = log_file.read()

            # Check that the log file contains the expected message
            self.assertIn("Model training job complete.", log_contents)

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

    def tearDown(self):
        # Restore the logs
        with open(data_loading_log, 'w') as f:
            f.write(self.data_loading_log_content)
        with open(scheduler_log, 'w') as f:
            f.write(self.scheduler_log_content)
        with open(data_collection_log, 'w') as f:
            f.write(self.data_collection_log_content)
        with open(models_training_log, 'w') as f:
            f.write(self.models_training_log_content)


if __name__ == '__main__':
    unittest.main()
