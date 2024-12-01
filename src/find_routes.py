from rdflib import URIRef
from rdflib.namespace import Namespace, RDFS
from data_processing import calculate_distance

EX = Namespace('http://example.com/gtfs#')

def find_routes(g, origin_stops, destination_stops):
    """
    Find every possible path between two nodes in the graph, doing at most one transfer.

    A path is defined by two rules:
    1) origin and destination are directly connected by one line.
    2) there are two stops between the origin and destination, close to each other,
    so that one is directly connected to the origin and the other is directly connected to the destination.
    
    Args:
    RDF Graph: graph that represents the transport network
    List: list of stops near the origin
    List: list of stops near the destination
    
    Returns:
    List: list of all possible paths. Each path is a tuple with fields:
    origin, origin_route, mid_stop_1, mid_stop_2, destination_route and destination
    """
    paths = []
    for origin in origin_stops:
        origin = URIRef('http://example.com/gtfs#' + origin)
        for destination in destination_stops:
            destination = URIRef('http://example.com/gtfs#' + destination)
            for origin_route in g.objects(URIRef(origin), URIRef(EX.has_route)):
                for destination_route in g.objects(URIRef(destination), URIRef(EX.has_route)):
                    if origin_route == destination_route:
                        paths.append((origin, origin_route, origin, origin, destination_route, destination))
                    else:
                        for mid_stop_1 in g.subjects(URIRef(EX.has_route), origin_route):
                            for transfer in g.subjects(URIRef(EX.has_transfer_from), mid_stop_1):
                                mid_stop_2 = g.value(transfer, URIRef(EX.has_transfer_to))
                                for route in g.objects(mid_stop_2, URIRef(EX.has_route)):
                                    if route == destination_route:
                                        paths.append((origin, origin_route, mid_stop_1, mid_stop_2, destination_route, destination))           
    return paths

def get_stop_coordinates(g, stop):
    """
    Get the geographic coordinates of a stop.
    
    Args:
    RDF Graph: graph that represents the transport network
    URIRef: a Stop instance of the graph
    
    Returns:
    Tuple: couple of floats representing latitude and longitude
    """
    lat = g.value(stop, URIRef(EX.has_latitude))
    lon = g.value(stop, URIRef(EX.has_longitude))
    return (float(lat), float(lon))
                                                   
def get_route_mode(g, route):
    """
    Get the transport mode (subway, light subway, rail, city bus, intercity bus) of a route.
    
    Args:
    RDF Graph: graph that represents the transport network
    URIRef: a Route instance of the graph
    
    Returns:
    URIRef: a Mode instance of the graph
    """
    mode = g.value(route, URIRef(EX.has_mode))
    return mode

def get_label(g, instance):
    """
    Get the label of an instance of the graph.
    
    Args:
    RDF Graph: graph that represents the transport network
    URIRef: an instance of the graph
    
    Returns:
    String: the label of the instance
    """
    label = g.value(instance, URIRef(RDFS.label))
    return label

def find_path_distance(g, path):
    """
    Calculate the distance between the origin and the destination.

    the distance is calculated by adding the distances between each pair of the stops
    that make up the route and are directly connected. Paths without transfers are preferable.
    
    Args:
    RDF Graph: graph that represents the transport network
    Tuple: a path, which is a tuple with fields origin, origin_route, mid_stop_1, mid_stop_2,
    destination_route and destination
    
    Returns:
    Float: distance of the path
    """
    distance = 0
    origin, origin_route, mid_stop_1, mid_stop_2, destination_route, destination = path
    # paths without transfers are preferable
    if origin == mid_stop_1:
        distance = -0.6
    origin_lat, origin_lon = get_stop_coordinates(g, origin)
    mid_stop_1_lat, mid_stop_1_lon = get_stop_coordinates(g, mid_stop_1)
    mid_stop_2_lat, mid_stop_2_lon = get_stop_coordinates(g, mid_stop_2)
    destination_lat, destination_lon = get_stop_coordinates(g, destination)
    distance += calculate_distance(origin_lat, origin_lon, mid_stop_1_lat, mid_stop_1_lon)
    distance += calculate_distance(mid_stop_1_lat, mid_stop_1_lon, mid_stop_2_lat, mid_stop_2_lon)
    distance += calculate_distance(mid_stop_2_lat, mid_stop_2_lon, destination_lat, destination_lon)
    return distance

def find_best_routes(g, paths):
    """
    Show on screen the shortest paths to go from source to destination.

    Orders the list of all possible paths returned by the function find_routes according to the distance
    calculated by the function find_path_distance. 
    If the distance of a path is greater than the distance of the shortest path plus 2 kilometer,
    don't consider the path. If two paths use the same mode for the origin and destination routes,
    only the shortest one is considered.
    
    Args:
    RDF Graph: graph that represents the transport network
    List: the list of all possible paths.
    
    Returns:
    Void
    """
    route_modes = set()
    paths = sorted(paths, key=lambda path: find_path_distance(g, path))    
    shortest_path_distance = find_path_distance(g, paths[0])
    origin, origin_route, mid_stop_1, mid_stop_2, destination_route, destination = paths[0]
    origin = get_label(g, origin)
    origin_route_mode = get_route_mode(g, origin_route)
    origin_route_mode = get_label(g, origin_route_mode)
    # Differenciate between city and intercity bus
    if (origin_route.startswith('http://example.com/gtfs#8')):
        origin_route_mode += ' intercity'
    origin_route = get_label(g, origin_route)
    mid_stop_1 = get_label(g, mid_stop_1)
    mid_stop_2 = get_label(g, mid_stop_2)
    destination = get_label(g, destination)
    destination_route_mode = get_route_mode(g, destination_route)
    destination_route_mode = get_label(g, destination_route_mode)
    # Differenciate between city and intercity bus
    if (destination_route.startswith('http://example.com/gtfs#8')):
        destination_route_mode += ' intercity'
    destination_route = get_label(g, destination_route)
    route_modes.add('{}#{}'.format(origin_route_mode, destination_route_mode))
    print('{} >> {}#{} ({} >> {}) >> {}#{} >> {}'.format(origin, origin_route_mode, origin_route, mid_stop_1, mid_stop_2,
                                                         destination_route_mode, destination_route, destination))
    for path in paths[1:]:
        path_distance = find_path_distance(g, path)
        # don't consider the path if its distance is greater than shortest_path_distance + 2 km
        if (path_distance > shortest_path_distance + 2):
            continue
        origin, origin_route, mid_stop_1, mid_stop_2, destination_route, destination = path
        origin = get_label(g, origin)
        origin_route_mode = get_route_mode(g, origin_route)
        origin_route_mode = get_label(g, origin_route_mode)
        # Differenciate between city and intercity bus
        if (origin_route.startswith('http://example.com/gtfs#8')):
            origin_route_mode += ' intercity'
        origin_route = get_label(g, origin_route)
        mid_stop_1 = get_label(g, mid_stop_1)
        mid_stop_2 = get_label(g, mid_stop_2)
        destination = get_label(g, destination)
        destination_route_mode = get_route_mode(g, destination_route)
        destination_route_mode = get_label(g, destination_route_mode)
        # Differenciate between city and intercity bus
        if (destination_route.startswith('http://example.com/gtfs#8')):
            destination_route_mode += ' intercity'
        destination_route = get_label(g, destination_route)
        # if origin_route_mode and destination_route_mode have been already seen together, we discard this path
        route_mode = '{}#{}'.format(origin_route_mode, destination_route_mode)
        if (route_mode in route_modes):
            continue
        route_modes.add(route_mode)
        print('{} >> {}#{} ({} >> {}) >> {}#{} >> {}'.format(origin, origin_route_mode, origin_route, mid_stop_1, mid_stop_2,
                                                         destination_route_mode, destination_route, destination))
        
