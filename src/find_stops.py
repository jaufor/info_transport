import pandas as pd
import numpy as np
from data_processing import calculate_distance

def find_nearest_stops(lat, lon):
    """
    Get stops that are near a given location.

    Args:
    Float: latitude coordinate of a location
    Float: longitude coordinate of a location
    
    Returns:
    List: stop_id of nearby stops
    """
    stops = pd.read_csv('data/processed/stops.csv')
    stops = pd.DataFrame(stops, columns=['stop_id', 'stop_lat', 'stop_lon'])
    # calculate distance between the input location and each stop
    stops['distance'] = calculate_distance(lat, lon, stops['stop_lat'], stops['stop_lon'])
    # filter stops that are less than 0.25 kilometres and sorter them according to distance
    stops_nearest = stops[stops.distance < 0.25].sort_values(by='distance', ascending=True)
    stops_nearest = stops_nearest['stop_id'].to_list()
    return stops_nearest
