import csv
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import Namespace, NamespaceManager, RDF, RDFS, XSD

EX = Namespace('http://example.com/gtfs#')

def add_routes(g, filename):
    """
    Read filename with routes and add them to the RDF graph.

    Args:
    RDF Graph: graph to which the routes have to be added
    String: path to the filename with the routes

    Returns:
    RDF graph: input RDF graph with routes added
    """
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            route = URIRef(EX[row['route_id']])
            g.add((route, RDF.type, URIRef(EX.Route)))        
            g.add((route, RDFS.label, Literal(row['route_short_name'])))
            g.add((route, RDFS.comment, Literal(row['route_long_name'])))
            g.add((route, EX.has_mode, URIRef(EX[row['route_type']])))        
    return g

def add_stops(g, filename):
    """
    Read filename with stops and add them to the RDF graph.

    Args:
    RDF Graph: graph to which the stops have to be added
    String: path to the filename with the stops

    Returns:
    RDF graph: input RDF graph with stops added
    """
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stop = URIRef(EX[row['stop_id']])
            g.add((stop, RDF.type, URIRef(EX.Stop)))        
            g.add((stop, RDFS.label, Literal(row['stop_name'])))
            g.add((stop, EX.has_route, URIRef(EX[row['route_id']])))
            g.add((stop, EX.has_latitude, Literal(row['stop_lat'], datatype=XSD.decimal)))
            g.add((stop, EX.has_longitude, Literal(row['stop_lon'], datatype=XSD.decimal)))
    return g

def add_transfers(g, filename):
    """
    Read filename with transfers and add them to the RDF graph.

    Args:
    RDF Graph: graph to which the transfers have to be added
    String: path to the filename with the transfers

    Returns:
    RDF graph: input RDF graph with transfers added
    """
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transfer = URIRef(EX[row['transfer_id']])
            g.add((transfer, RDF.type, URIRef(EX.Transfer)))
            g.add((transfer, EX.has_transfer_from, URIRef(EX[row['transfer_from']])))
            g.add((transfer, EX.has_transfer_to, URIRef(EX[row['transfer_to']])))
            g.add((transfer, EX.has_distance, Literal(row['distance'], datatype=XSD.decimal)))
    return g

