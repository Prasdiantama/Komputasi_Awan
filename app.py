from flask import Flask, request, jsonify, render_template
from google.cloud import bigquery
import os
import logging
import numpy as np

app = Flask(__name__)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:/tahan/tugas_cloud/project-saya-426408-0a5aaf021b49.json"

client = bigquery.Client()

def get_column_values(column_name):
    query = f"SELECT DISTINCT `{column_name}` FROM `project-saya-426408.data_kelulusan.Kelulusan`"
    query_job = client.query(query)
    results = query_job.result()
    return [row[column_name] for row in results]

def get_total_students(filters):
    query = "SELECT COUNT(*) as total FROM `project-saya-426408.data_kelulusan.Kelulusan`"
    if filters:
        filter_conditions = [f"`{key}` IN UNNEST(@{key})" for key in filters]
        query += " WHERE " + " AND ".join(filter_conditions)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter(key, "STRING", value)
            for key, value in filters.items()
        ]
    )
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()
    return int(results.to_dataframe().iloc[0]["total"])

def get_average_gpa(filters):
    query = "SELECT CAST(`IPK` AS FLOAT64) as gpa FROM `project-saya-426408.data_kelulusan.Kelulusan`"
    if filters:
        filter_conditions = [f"`{key}` IN UNNEST(@{key})" for key in filters]
        query += " WHERE " + " AND ".join(filter_conditions)
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter(key, "STRING", value)
            for key, value in filters.items()
        ]
    )
    query_job = client.query(query, job_config=job_config)
    results = query_job.result().to_dataframe()
    if results.empty:
        return None
    gpa_values = results['gpa'].to_numpy()
    return float(np.mean(gpa_values))

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
        logging.error(f"Error fetching options for column {column_name}: {str(e)}")
        return str(e), 500

@app.route('/get-stats', methods=['POST'])
def get_stats():
    filters = request.json.get('filters', {})
    try:
        total_students = get_total_students(filters)
        average_gpa = get_average_gpa(filters)
        return jsonify({'total_students': total_students, 'average_gpa': average_gpa})
    except Exception as e:
        logging.error(f"Error fetching stats with filters {filters}: {str(e)}")
        return str(e), 500

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(port=5000, debug=True)
