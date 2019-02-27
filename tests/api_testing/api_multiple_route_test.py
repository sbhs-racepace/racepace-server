from client import TestApiClient


client = TestApiClient()

waypoints = ["-33.892237, 151.220249", '-33.892101, 151.211785', '-33.883380, 151.207635', '-33.876070, 151.218543']

route = client.get_multiple_route(waypoints)

print(route)        