import unittest
import time
import os
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from .app import app

# Data Loading log file path
data_loading_log = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs/data_loading.log')


def start_app():
    app.run()


class TestApp(unittest.TestCase):
    def setUp(self):
        # Create a process for the Flask app
        self.app_process = multiprocessing.Process(target=start_app)
        self.app_process.start()

        time.sleep(2)

        # Set up the Selenium driver
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--remote-debugging-pipe')
        self.driver = webdriver.Chrome(options=chrome_options)

        # Clear the logs before each test
        open(data_loading_log, 'w').close()

    def test_home_page(self):
        self.driver.get('http://127.0.0.1:5000/')
        WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.hero-title'))
        )
        self.assertEqual(self.driver.current_url, 'http://127.0.0.1:5000/')

    def test_workouts_page(self):
        self.driver.get('http://127.0.0.1:5000/workouts')
        WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#workout-table'))
        )
        self.assertEqual(self.driver.current_url, 'http://127.0.0.1:5000/workouts')

        # Check the logs
        with open(data_loading_log, 'r') as f:
            log_content = f.read()
            self.assertIn('Workout data loaded.', log_content)

    def test_my_exercises_page(self):
        self.driver.get('http://127.0.0.1:5000/my-exercises')
        WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#exercise-table'))
        )
        self.assertEqual(self.driver.current_url, 'http://127.0.0.1:5000/my-exercises')

        # Check the logs
        with open(data_loading_log, 'r') as f:
            log_content = f.read()
            self.assertIn('Filtered exercise data loaded.', log_content)

    def test_analytics_page(self):
        self.driver.get('http://127.0.0.1:5000/analytics')
        # Add a check for an element that should be present on the analytics page

    def tearDown(self):
        self.driver.quit()
        self.app_process.terminate()


if __name__ == '__main__':
    unittest.main()
