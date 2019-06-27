from client import TestApiClient


client = TestApiClient()
waypoints = [
    "-33.892098, 151.216802",
    "-33.886053, 151.218030",
    "-33.880612, 151.216838",
]
route = client.get_multiple_route(waypoints)
print(route)
