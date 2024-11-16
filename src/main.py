from rdflib import Graph
from rdflib.namespace import Namespace, NamespaceManager, RDF, RDFS, XSD
from data_reading import add_routes, add_stops, add_transfers
from find_coordinates import get_coordinates
from find_stops import find_nearest_stops
from find_routes import find_routes, find_best_routes

# create graph
EX = Namespace('http://example.com/gtfs#')
namespace_manager = NamespaceManager(Graph())
namespace_manager.bind('ex', EX, override=False)
namespace_manager.bind('rdfs', RDFS, override=False)
namespace_manager.bind('xsd', XSD, override=False)
g = Graph()
g.namespace_manager = namespace_manager

# load ontology and populate it
g.parse('data/ontology/gtfs.ttl')
g = add_routes(g, 'data/processed/routes.csv')
g = add_stops(g, 'data/processed/stops.csv')
g = add_transfers(g, 'data/processed/transfers.csv')

# ask for the origin address, must be from the Community of Madrid
print('Which is the origin address?')
street = input('street name: ')
housenumber = input('house number: ')
street = housenumber + ' ' + street
city = input('city name: ')
query = {'street': street, 'city': city}
# get geographic coordinates of origin address
lat, lon = get_coordinates(query)
# find stops near origin
origin_stops = find_nearest_stops(lat, lon)

# ask for the destination address, must be from the Community of Madrid
print('Which is the destination address?')
street = input('street name: ')
housenumber = input('house number: ')
street = housenumber + ' ' + street
city = input('city name: ')
query = {'street': street, 'city': city}
# get geographic coordinates of destination address
lat, lon = get_coordinates(query)
# find stops near destination
destination_stops = find_nearest_stops(lat, lon)

# find best paths between origin and destination
paths = find_routes(g, origin_stops, destination_stops)
best_paths = find_best_routes(g, paths)
print (best_paths)

# close the graph
g.close()
