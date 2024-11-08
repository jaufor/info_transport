import pandas as pd
import numpy as np
import re

def read_routes(input_path):
    """
    Get the Routes from one GTFS data source.

    Args:
    String: path to the GTFS data source.

    Returns:
    Pandas dataframe with columns: 'route_id', 'route_short_name', 'route_long_name' and 'route_type'.
    """
    routes = pd.read_csv(input_path + "routes.txt")
    columns = ['route_id', 'route_short_name', 'route_long_name', 'route_type']
    routes = pd.DataFrame(routes, columns=columns)
    routes['route_type'] = 'mode_' + routes['route_type'].astype(str)
    return routes

def read_accesses(input_path):
    """
    Get the accesses to stops from one GTFS data source.

    Geographic coordinates of the stops are not correct in the subway and light subway data sources.
    It is needed to replace them with the geographic coordinates of the corresponding accesses.

    Args:
    String: path to the GTFS data source.

    Returns:
    Pandas dataframe with columns: 'stop_id', 'access_lat' and 'access_lon'.
    """
    pattern = r'acc_(\d+_\d+)_\d+'
    accesses = pd.read_csv(input_path + "stops.txt")
    accesses = accesses[accesses.location_type == 2]
    columns = ['stop_id', 'stop_lat', 'stop_lon']
    accesses = pd.DataFrame(accesses, columns=columns)
    accesses['stop_id'] = accesses['stop_id'].apply(lambda x: 'par_' + re.search(pattern, x).group(1) if re.search(pattern, x) else None)
    accesses.drop_duplicates(subset=['stop_id'], inplace=True)
    accesses.rename(columns={'stop_lat': 'access_lat', 'stop_lon': 'access_lon'}, inplace=True)
    return accesses

def read_parent_stops(input_path):
    """
    Get the parent stops from one GTFS data source.

    Geographic coordinates of the stops are not correct in the subway and light subway data sources.
    If the stop has no accesses but has a parent_station that is also a stop, then get this parent stop.
    Later, it will be needed to get the correct geographic coordinates from the accesses to the parent stop.
    It only happens for the subway data source.

    Args:
    String: path to the GTFS data source.

    Returns:
    Pandas dataframe with columns: 'stop_id' and 'parent_stop'.
    """
    pattern = r'est_4_(\d+)'
    parent_stops = pd.read_csv(input_path + "stops.txt")
    parent_stops = parent_stops[parent_stops.location_type == 0]
    # there is a parent station
    parent_stops = parent_stops[~parent_stops['parent_station'].isnull()]
    # the parent station is also a stop
    parent_stops = parent_stops[parent_stops['parent_station'].str.startswith('est_4_')]
    columns = ['stop_id', 'parent_station']
    parent_stops = pd.DataFrame(parent_stops, columns=columns)
    # replace the parent_station for the parent stop
    parent_stops['parent_station'] = parent_stops['parent_station'].apply(lambda x: 'par_4_' + re.search(pattern, x).group(1) if re.search(pattern, x) else None)    
    parent_stops.rename(columns={'parent_station': 'parent_stop'}, inplace=True)
    return parent_stops
    
def read_stops(input_path, routes):
    """
    Get the stops from one GTFS data source.

    To link each stop with its route, it's needed to merge data from four sources:
    stops, stop_times, trips and routes.

    Args:
    String: path to the GTFS data source.
    Pandas dataframe: routes

    Returns:
    Pandas dataframe with columns: 'stop_id' and 'stop_name', 'stop_lat', 'stop_lon' and 'route_id'.
    """
    # stop_times
    stop_times = pd.read_csv(input_path + "stop_times.txt")
    columns = ['trip_id', 'stop_id']
    stop_times = pd.DataFrame(stop_times, columns=columns).drop_duplicates(subset=['stop_id'])
    # trips
    trips = pd.read_csv(input_path + "trips.txt")
    columns = ['route_id', 'trip_id']
    trips = pd.DataFrame(trips, columns=columns)
    trips = trips.merge(routes)
    # stops
    stops = pd.read_csv(input_path + "stops.txt")
    stops = stops[stops.location_type == 0]
    columns = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon']
    stops = pd.DataFrame(stops, columns=columns)
    stops = stops.merge(stop_times)
    stops = stops.merge(trips)
    columns = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'route_id']
    stops = pd.DataFrame(stops, columns=columns)
    return stops

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Get the distance between two geographic locations.

    Args:
    String: geographic latitude of first point in radians
    String: geographic longitude of first point in radians
    String: geographic latitude of second point in radians
    String: geographic longitude of second point in radians    

    Returns:
    Float: distance in kilometers
    """
    array = np.sin(lat1) * np.sin(lat2) + np.cos(lat1) * np.cos(lat2) * np.cos(lon1 - lon2)
    # following instruction is needed to avoid RuntimeWarning: invalid value encountered in arccos 
    array = np.where(array <= 1, array, 1)                           
    return 6371.01 * np.arccos(array)

def same_line(stops: pd.DataFrame, stop1, stop2):
    """
    find out if two stops belong to the same line

    Args:
    Pandas dataframe: stops
    String: stop_id of the first stop
    String: stop_id of the second stop

    Returns:
    Boolean: true if both stops belong to the same line, false otherwise
    """
    route_id1 = stops.loc[stops['stop_id'] == stop1, 'route_id'].iloc[0]
    route_id2 = stops.loc[stops['stop_id'] == stop2, 'route_id'].iloc[0]
    return route_id1 == route_id2

def find_transfers(stops: pd.DataFrame):
    """
    find the stops that are close to each other, thus one can walk from one to the other.

    Args:
    Pandas dataframe: stops

    Returns:
    Pandas dataframe with columns: 'transfer_id', 'transfer_from', 'transfer_to' and 'distance'
    """
    geo_coords = pd.DataFrame(stops, columns=['stop_id', 'stop_lat', 'stop_lon'])
    geo_coords = geo_coords.set_index('stop_id')
    geo_coords.index.name = None
    # to calculate the distance between two points, geographic coordinates need to be in radians
    geo_coords['stop_lat'] = np.deg2rad(geo_coords['stop_lat'])
    geo_coords['stop_lon'] = np.deg2rad(geo_coords['stop_lon'])
    # calculate the distance between each pair of stops
    lat1 = geo_coords['stop_lat'].values[:, None]  
    lon1 = geo_coords['stop_lon'].values[:, None]  
    lat2 = geo_coords['stop_lat'].values[None, :]  
    lon2 = geo_coords['stop_lon'].values[None, :]  
    distances_array = calculate_distance(lat1, lon1, lat2, lon2)
    distances = pd.DataFrame(distances_array, index=geo_coords.index, columns=geo_coords.index)
    transfers = (
        # filter distances below 0.5 kilometers
        # and discard reflexive transfers
        distances[distances < 0.5][distances > 0]
        .stack()
        .reset_index()
        .rename(columns={0: 'distance', 'level_0': 'transfer_from', 'level_1': 'transfer_to'})
       )
    # discard transfers between stops of the same line
    transfers['same_line'] = transfers.apply(lambda x: same_line(stops, x['transfer_from'], x['transfer_to']), axis=1)
    transfers = transfers.drop(transfers[transfers['same_line']].index)
    # generate a transfer_id
    transfers['transfer_id'] = transfers['transfer_from'].astype(str) + '_to_' + transfers['transfer_to'].astype(str)
    transfers = transfers[['transfer_id', 'transfer_from', 'transfer_to', 'distance']]
    return transfers

# Process subway data source
routes = read_routes('data/raw/crtm/M4/')
routes.to_csv('data/processed/routes.csv', index=False)
accesses = read_accesses('data/raw/crtm/M4/')
accesses.to_csv('data/processed/accesses.csv', index=False)
# get the parent stops
parent_stops = read_parent_stops('data/raw/crtm/M4/')
# get the parent stop geographic coordinates from its accesses
parent_stops = parent_stops.merge(accesses, left_on='parent_stop', right_on='stop_id', how="left")
parent_stops.rename(columns={'stop_id_x': 'stop_id'}, inplace=True)
parent_stops.drop(columns=['parent_stop', 'stop_id_y'], inplace=True)
parent_stops.to_csv('data/processed/parent_stops.csv', index=False)
# concatenate the geographic coordinates of the accesses and the parent stops
accesses = pd.concat([accesses, parent_stops], ignore_index=True)
stops = read_stops('data/raw/crtm/M4/', routes)
# replace geographic coordinates of stops for those of the accesses
stops = stops.merge(accesses, on='stop_id', how="left")
stops['stop_lat'] = np.where(np.isnan(stops['access_lat']), stops['stop_lat'], stops['access_lat'])
stops['stop_lon'] = np.where(np.isnan(stops['access_lon']), stops['stop_lon'], stops['access_lon'])
columns = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'route_id']
stops = pd.DataFrame(stops, columns=columns)
stops.to_csv('data/processed/stops.csv', index=False)

# Process rail data source
#routes = read_routes('data/raw/renfe/M5/')
#routes.to_csv('data/processed/routes.csv', index=False, header=False, mode='a')
#stops = read_stops('data/raw/renfe/M5/', routes)
#columns = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'route_id']
#stops = pd.DataFrame(stops, columns=columns)
#stops.to_csv('data/processed/stops.csv', index=False, header=False, mode='a')

# Process city bus data source
#routes = read_routes('data/raw/crtm/M6/')
#routes.to_csv('data/processed/routes.csv', index=False, header=False, mode='a')
#stops = read_stops('data/raw/crtm/M6/', routes)
#columns = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'route_id']
#stops = pd.DataFrame(stops, columns=columns)
#stops.to_csv('data/processed/stops.csv', index=False, header=False, mode='a')

# Process light subway data source
#routes = read_routes('data/raw/crtm/M10/')
#routes.to_csv('data/processed/routes.csv', index=False, header=False, mode='a')
#accesses = read_accesses('data/raw/crtm/M10/')
#accesses.to_csv('data/processed/accesses.csv', index=False)
#stops = read_stops('data/raw/crtm/M10/', routes)
# replace geographic coordinates of stops for those of the accesses
#stops = stops.merge(accesses, on='stop_id', how="left")
#stops['stop_lat'] = np.where(np.isnan(stops['access_lat']), stops['stop_lat'], stops['access_lat'])
#stops['stop_lon'] = np.where(np.isnan(stops['access_lon']), stops['stop_lon'], stops['access_lon'])
#columns = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'route_id']
#stops = pd.DataFrame(stops, columns=columns)
#stops.to_csv('data/processed/stops.csv', index=False, header=False, mode='a')

# Process intercity bus data source
#routes = read_routes('data/raw/crtm/M89/')
#routes.to_csv('data/processed/routes.csv', index=False, header=False, mode='a')
#stops = read_stops('data/raw/crtm/M89/', routes)
#columns = ['stop_id', 'stop_name', 'stop_lat', 'stop_lon', 'route_id']
#stops = pd.DataFrame(stops, columns=columns)
#stops.to_csv('data/processed/stops.csv', index=False, header=False, mode='a')

# Find and save transfers
#stops = pd.read_csv('data/processed/stops.csv')
#transfers = find_transfers(stops)
#transfers.to_csv('data/processed/transfers.csv', index=False)
