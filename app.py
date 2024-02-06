from flask import Flask, jsonify, render_template
import pandas as pd

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/workouts')
def workouts():
    # Load the workout data
    workouts = pd.read_csv('data/current/workout_data.csv')

    # Convert the DataFrame to JSON and return it
    return jsonify(workouts.to_dict(orient='records'))


if __name__ == '__main__':
    app.run(debug=True)
