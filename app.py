from flask import Flask, request, jsonify, render_template
from google.cloud import bigquery
import os

app = Flask(__name__)

# Set the path to your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/tugas_cloud/project-saya-426408-0a5aaf021b49.json"

client = bigquery.Client()

def get_column_values(column_name):
    query = f"SELECT DISTINCT `{column_name}` FROM `project-saya-426408.data_kelulusan.Kelulusan`"
    query_job = client.query(query)
    results = query_job.result()
    return [row[column_name] for row in results]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-options', methods=['GET'])
def get_options():
    column_name = request.args.get('columnName')
    try:
        options = get_column_values(column_name)
        return jsonify(options)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
