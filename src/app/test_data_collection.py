import unittest
import pandas as pd
import os

from .data_collection import collect_workout_data

# Data Collection log file path
data_collection_log = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs/data_collection.log')


class TestDataCollection(unittest.TestCase):

    def setUp(self):
        # Create test data files
        self.workout_data = [{'DATE': '2022-01-01', 'WORKOUT': 'Workout 1', 'EXERCISE': 'Exercise 1'}]

        # Create a test directory if it doesn't exist
        if not os.path.exists('test'):
            os.mkdir('test')

        # Save the test data to the test directory
        pd.DataFrame(self.workout_data).to_csv('test/workout_2024-01-01.csv', index=False)

        # Save the logs to memory
        with open(data_collection_log, 'r') as f:
            self.data_collection_log_content = f.read()

    def tearDown(self):
        # Delete test data files
        os.remove('test/workout_2024-01-01.csv')
        os.remove('test/workout_data.csv')

        # Delete test data directory
        os.rmdir('test')

        # Restore the logs
        with open(data_collection_log, 'w') as f:
            f.write(self.data_collection_log_content)

    def test_collect_workout_data(self):
        # Call the function with the known input
        result1 = collect_workout_data(input_path='test', output_path='test')

        # Read the saved workout data
        result2 = pd.read_csv('test/workout_data.csv', header=0)

        # Define the expected result
        expected_result = pd.DataFrame(self.workout_data)

        # Assert that the results match the expected result
        pd.testing.assert_frame_equal(result1, expected_result)
        pd.testing.assert_frame_equal(result2, expected_result)


if __name__ == '__main__':
    unittest.main()
