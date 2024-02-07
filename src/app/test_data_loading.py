import unittest
import os
import pandas as pd

from src.app.data_loading import load_workout_data, load_filtered_exercise_data


class TestDataLoading(unittest.TestCase):

    def setUp(self):
        # Create test data files
        workout_data = [{'DATE': '2022-01-01', 'WORKOUT': 'Workout 1', 'EXERCISE': 'Exercise 1'}]
        exercise_data = [{'Title': 'Exercise 1', 'Desc': 'Description 1', 'RatingDesc': 'RatingDesc 1'}]

        pd.DataFrame(workout_data).to_csv('workout_data.csv', index=False)
        pd.DataFrame(exercise_data).to_csv('workout_exercises.csv', index=False)

    def tearDown(self):
        # Delete test data files
        os.remove('workout_data.csv')
        os.remove('workout_exercises.csv')

    def test_load_workout_data(self):
        # Define a known input file path
        input_file_path = 'workout_data.csv'

        # Call the function with the known input
        result = load_workout_data(file_path=input_file_path)

        # Define the expected result
        expected_result = [{'DATE': '2022-01-01', 'WORKOUT': 'Workout 1', 'EXERCISE': 'Exercise 1'}]

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)

    def test_load_filtered_exercise_data(self):
        # Define a known input file path
        input_file_path = 'workout_exercises.csv'

        # Call the function with the known input
        result = load_filtered_exercise_data(file_path=input_file_path)

        # Define the expected result
        expected_result = [{'Title': 'Exercise 1', 'Desc': 'Description 1'}]

        # Assert that the result matches the expected result
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
