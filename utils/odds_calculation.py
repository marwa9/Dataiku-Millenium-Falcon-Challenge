# -*- coding: utf-8 -*-
"""
@author: Marwa
"""

import numpy as np


def get_key(dictionary, search_value):
    for key, value in dictionary.items():
        if value == search_value:
            return key
    # If value is not found, raise an exception
    raise ValueError(f'Value {search_value} not found in the dictionary.')
          
# Verify possible paths given autonomy and countdown information
def paths_verification(autonomy,countdown,dict_planets,all_paths,edges_distances):
    possible_paths = []
    inter_distances = []
    arrival_margins = []
    for path in all_paths:
        inter_dist_planets = []
        for i in range(len(path)-1):
            inter_dist_planets.append(edges_distances[get_key(dict_planets,path[i])+get_key(dict_planets,path[i+1])])
            
        s = np.array(inter_dist_planets).sum()
        refuel = s // autonomy
        arrival_margin = countdown - (s+refuel)
        # Discard paths requiring more days than countdown, or with edges whose distance > autonomy 
        if not(all(i <= autonomy for i in inter_dist_planets)) or (arrival_margin<0):
            continue
        else:
            possible_paths.append(path)
            inter_distances.append(inter_dist_planets)
            arrival_margins.append(arrival_margin)
    return possible_paths,inter_distances,arrival_margins

# Find the best way to reach arrival planet i.e., avoid being captured by bounting hunters
# as much as possible
def capture_frequency(possible_paths,inter_distances,arrival_margins,
                      dict_planets,bounty_hunters_dict):
    captured_times = []
    for i,path in enumerate(possible_paths):
        j = 0 # variable to identify where the Millennium Falcon is currently parked  
        arrival_day = inter_distances[i][0]
        wait_capacity = arrival_margins[i]
        schedule_dict = dict()
        k = 0 # variable of capture frequency in path i
        while j<len(inter_distances[i])-1:     
            if (get_key(dict_planets,path[j+1]) in bounty_hunters_dict[str(arrival_day)]) and (wait_capacity>0):
                wait_capacity -=1
                arrival_day +=1
            else:
                if j==0:
                    schedule_dict[arrival_day] = get_key(dict_planets,path[j+1]) 
                arrival_day +=1
                schedule_dict[arrival_day] = get_key(dict_planets,path[j+1])                     
                j +=1    
        for key in schedule_dict.keys():
            if schedule_dict[key] in bounty_hunters_dict[str(key)]:
                k +=1           
        captured_times.append(k) 
    return min(captured_times) # Take the min to consider only the optimized path

def capture_probability(k):
    if k == 0:
        return 0
    somme = 0
    for i in range(k):
        somme += 9**i/10**(i+1)
    return somme