# -*- coding: utf-8 -*-
"""
@author: Marwa Kechaou
"""

import json
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

""" Define the backend URL, identified after running backend.py """
# Two addresses are displayed. The second one represents the IP address 
# to the one where my Flask app is running
backend_url = "http://192.168.30.52:5000"  

# Read config_backend json file and prepare millennium_falcon_data 
try:
    with open('config_files/config_backend.json', 'r') as json_file:
        data_config_backend = json.load(json_file)
        
    with open(data_config_backend["millennium_falcon_path"], 'r') as mf_file:
        millennium_falcon_data = json.load(mf_file)
        
    millennium_falcon_data = {"task": 1, "data" : millennium_falcon_data, "routes_db_path": data_config_backend['routes_db_path']}
        
except Exception as e:
    print(f"Error reading JSON files: {str(e)}")
    exit(1)
    

# Route to the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the file upload and odds calculation
@app.route('/calculate_odds', methods=['POST'])
def compute_odds():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':  
            empire_data = {"task": 2, "data" : json.loads(file.read().decode('utf-8'))}
            # Send files to the backend for odds calculation
            response = requests.post(f"{backend_url}/main", json={"millennium_falcon": millennium_falcon_data, 
                                                                            "empire": empire_data})
            if response.status_code == 200: # Check if the response is successful
                result = response.json()
                odds = result['odds']
                return jsonify({"odds": odds})

    return jsonify({"odds": "Error"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    
