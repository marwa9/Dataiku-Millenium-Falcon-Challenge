# -*- coding: utf-8 -*-
"""
@author: Marwa Kechaou
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from utils.graph_paths import get_bidirectional_edges,graph_construction,All_Paths_Departure_Arrival_bidirectionel
from utils.odds_calculation import paths_verification,capture_frequency,capture_probability


app = Flask("__name__")
CORS(app, resources={r"/*": {"origins": "http://localhost:8000"}})

loaded_millennium_falcon = None # Global variable to avoid redundant calculations 
                                # depending solely on millennium_falcon file when using front-end

# Define a route to read the "millennium-falcon.json" file
@app.route('/read_millennium_falcon', methods=['POST'])
def read_millennium_falcon():
    data = request.get_json()
    millennium_falcon_dict = data.get("millennium_falcon")
    task = millennium_falcon_dict["task"]  
    if task == 1:
        millennium_falcon_data = millennium_falcon_dict["data"]
        autonomy = millennium_falcon_data["autonomy"]
        departure = millennium_falcon_data["departure"]
        arrival = millennium_falcon_data["arrival"]
        routes_db_path =  millennium_falcon_dict["routes_db_path"]
        routes_db = os.path.join(routes_db_path,millennium_falcon_data["routes_db"])
        return jsonify({"autonomy": autonomy,
                        "departure": departure,
                        "arrival": arrival,
                        "routes_db":routes_db})
    else:
        return jsonify({"Msg": "Error"})

# Define a route to read the "empire.json" file
@app.route('/read_empire', methods=['POST'])
def read_empire():
    data = request.get_json()
    empire_dict = data.get("empire")
    task = empire_dict["task"]
    if task == 2:
        data_empire = empire_dict['data']
        countdown = data_empire['countdown']
        bounty_hunters = data_empire['bounty_hunters']
        bounty_hunters_dict = dict()
        for i in range(countdown+1):
            bounty_hunters_dict[i] = []
        for d in bounty_hunters:
            if d['day']<= countdown:
                bounty_hunters_dict[d['day']].append(d['planet'])
        return jsonify({"countdown": countdown,
                        "bounty_hunters_dict":bounty_hunters_dict})
    else: 
        return jsonify({"Msg": "Error"})

# Read the sqlite file "routes_db"
def read_sqlite(database_path):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    # Retrieve data from the sqlite database
    cursor.execute("SELECT ORIGIN, DESTINATION, TRAVEL_TIME FROM ROUTES")
    results = cursor.fetchall()
    planets = []
    edges = []
    planets_distances = []
    for row in results:
        route = list(row)
        edges.append(route[:2])
        planets_distances.append(route[2])
        planets += route[:2]
    cursor.close()
    connection.close()  
    return planets,edges,planets_distances

# Create a dictionary to represent planets using numerical values that facilitate graph and path calculations. 
# Assign the departure planet the value 0, and the arrival planet the value len(planets)-1 as keys correspond to the planet names.
def planets_dictionary(planets,departure,arrival):
    dict_planets= dict()
    dict_planets[departure] = 0
    iterator = 1
    for p in planets:
        if not(p in [departure,arrival]):
            dict_planets[p] = iterator
            iterator +=1
    dict_planets[arrival] = len(planets)-1
    return dict_planets

@app.route('/find_all_paths', methods=['POST'])
def find_all_paths():
    # Read the millennium falcon json file
    response = read_millennium_falcon()
    # Check if the response is successful
    if response.status_code == 200:
        # Extract information from the JSON response
        data = response.json
        autonomy = data.get('autonomy')
        departure = data.get('departure')
        arrival = data.get('arrival')
        routes_db = data.get('routes_db')     
        # Extract information from the sqlite database
        planets, edges, planets_distances = read_sqlite(routes_db)
        # Identify edges of the graph formed by planets and their distances 
        bidirectional_edges,edges_distances = get_bidirectional_edges(edges,departure,arrival,planets_distances)  
        # Refer to planets by integers to facilitate paths search   
        planets = list(set(planets)) # remove redundant identified planets
        dict_planets = planets_dictionary(planets,departure,arrival)
        # Construct the graph from departure to arrival and find all paths connecting them
        graph = graph_construction(dict_planets,planets,bidirectional_edges)
        all_paths = All_Paths_Departure_Arrival_bidirectionel(graph)
        
        return jsonify({"autonomy": autonomy,
                        "dict_planets": dict_planets,
                        "all_paths": all_paths,
                        "edges_distances": edges_distances})   
    # Handle error case
    return jsonify({"Msg": "Error"})
    

@app.route('/compute_odds', methods=['POST'])
def compute_odds(autonomy,dict_planets,all_paths,edges_distances):
    response = read_empire()
    # Check if the response is successful
    if response.status_code == 200:
        # Extract information from the JSON response
        data = response.json
        countdown = data.get("countdown")
        bounty_hunters_dict = data.get("bounty_hunters_dict")
        possible_paths,inter_distances,arrival_margins = paths_verification(autonomy,countdown,dict_planets,all_paths,edges_distances)
        # Execute if possible_paths != [] otherwise odds = 0%
        if possible_paths != []:
            captured_times = capture_frequency(possible_paths,inter_distances,arrival_margins,
                                                dict_planets,bounty_hunters_dict)
            odds = 1 - capture_probability(captured_times)
            if odds<0: # If the  millennium falcon was captured several times
                odds = 0
        else:
            odds = 0   
        odds = 100*odds 
        return jsonify({"odds": odds}) 
    # Handle error case
    return jsonify({"Msg": "Error"})


@app.route('/main', methods=['POST'])  
def main():
    global loaded_millennium_falcon, autonomy, dict_planets, all_paths, edges_distances
    # Print the variable to check if calculations are repeated or not
    app.logger.debug("loaded_millennium_falcon: %s", loaded_millennium_falcon)
    # Check wether millennium_falcon has already been uploaded to avoid redundant find_all_paths calculations
    if loaded_millennium_falcon is None:
        response1 = find_all_paths()
        loaded_millennium_falcon = "Done"
        if response1.status_code == 200: # Check if the response is successful
            data1 = response1.json
            autonomy = data1.get("autonomy")
            dict_planets = data1.get("dict_planets")
            all_paths = data1.get("all_paths")
            edges_distances = data1.get("edges_distances")
            
    response2 = compute_odds(autonomy,dict_planets,all_paths,edges_distances)      
    if response2.status_code == 200:   
        data2 = response2.json
        odds = data2.get("odds")
        return jsonify({"odds": odds})
    # Handle error case
    return jsonify({"Msg": "Error"})
 
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0', threaded=True)