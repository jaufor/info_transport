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
    that make up the route and are directly connected.
    
    Args:
    RDF Graph: graph that represents the transport network
    Tuple: a path, which is a tuple with fields origin, origin_route, mid_stop_1, mid_stop_2,
    destination_route and destination
    
    Returns:
    Float: distance of the path
    """
    origin, origin_route, mid_stop_1, mid_stop_2, destination_route, destination = path
    origin_lat, origin_lon = get_stop_coordinates(g, origin)
    mid_stop_1_lat, mid_stop_1_lon = get_stop_coordinates(g, mid_stop_1)
    mid_stop_2_lat, mid_stop_2_lon = get_stop_coordinates(g, mid_stop_2)
    destination_lat, destination_lon = get_stop_coordinates(g, destination)
    distance = calculate_distance(origin_lat, origin_lon, mid_stop_1_lat, mid_stop_1_lon)
    distance += calculate_distance(mid_stop_1_lat, mid_stop_1_lon, mid_stop_2_lat, mid_stop_2_lon)
    distance += calculate_distance(mid_stop_2_lat, mid_stop_2_lon, destination_lat, destination_lon)
    return distance

def find_best_routes(g, paths):
    """
    Show on screen the three shortest paths to go from source to destination.

    Orders the list of all possible paths returned by the function find_routes according to the distance
    calculated by the function find_path_distance and shows the shortests paths on screen.
    If two paths contain the same trip (same line and same stops connected by it),
    only the shortest one is considered. 
    
    Args:
    RDF Graph: graph that represents the transport network
    List: the list of all possible paths to go from origin to destination doing one transfer at most
    
    Returns:
    Void
    """
    trips = set()
    paths = sorted(paths, key=lambda path: find_path_distance(g, path))
    for path in paths:
        origin, origin_route, mid_stop_1, mid_stop_2, destination_route, destination = path
        origin = get_label(g, origin)
        origin_route_mode = get_route_mode(g, origin_route)
        origin_route_mode = get_label(g, origin_route_mode)
        origin_route = get_label(g, origin_route)
        mid_stop_1 = get_label(g, mid_stop_1)
        mid_stop_2 = get_label(g, mid_stop_2)
        destination_route_mode = get_route_mode(g, destination_route)
        destination_route_mode = get_label(g, destination_route_mode)
        destination_route = get_label(g, destination_route)
        destination = get_label(g, destination)
        trip_1 = "{} - {}_L{} - {}".format(origin, origin_route_mode, origin_route, mid_stop_1)
        trip_2 = "{} - {}_L{} - {}".format(mid_stop_2, destination_route_mode, destination_route, destination)
        # if any of the two trips has been already seen, we discard this path
        if (trip_1 in trips) or (trip_2 in trips):
            continue
        trips.add(trip_1)
        trips.add(trip_2)
        print("{} - {}".format(trip_1, trip_2))