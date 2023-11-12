# -*- coding: utf-8 -*-
"""
@author: Marwa Kechaou
"""

import argparse
import requests
import json

# Define the command-line arguments
parser = argparse.ArgumentParser(description="Calculate the odds for Millennium Falcon")
parser.add_argument("millennium_falcon_file", help="Path to the millennium-falcon.json file")
parser.add_argument("empire_file", help="Path to the empire.json file")

args = parser.parse_args()

# Read the contents of the JSON files
try:
    with open(args.millennium_falcon_file, 'r') as mf_file:
        millennium_falcon_data = json.load(mf_file)
        
        with open('config_files/config_backend.json', 'r') as json_file:
            data_config_backend = json.load(json_file)
        millennium_falcon_data = {"task": 1, "data" : millennium_falcon_data, "routes_db_path": data_config_backend['routes_db_path']}

    with open(args.empire_file, 'r') as empire_file:
        empire_data = json.load(empire_file)
        empire_data = {"task": 2, "data" : empire_data}
except Exception as e:
    print(f"Error reading JSON files: {str(e)}")
    exit(1)

# Define the backend URL, identified after running backend.py
backend_url = "http://127.0.0.1:5000"

# Send the data to the backend for odds calculation
try:
    response = requests.post(f"{backend_url}/main", json={"millennium_falcon": millennium_falcon_data, "empire": empire_data})
    if response.status_code == 200: # Check if the response is successful
        result = response.json()
        odds = result["odds"]
        print(f"{odds}")
    else:
        print(response.status_code)
        print("Error calculating odds")

except requests.exceptions.RequestException as e:
    print(f"Error communicating with the backend: {str(e)}")
    exit(1)
