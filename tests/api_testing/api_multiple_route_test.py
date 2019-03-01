from client import TestApiClient


client = TestApiClient()
waypoints = ["-33.892545,151.219588","-33.892023,151.216920"]
#,"-33.886291, 151.217958"]

route = client.get_route(start="-33.892545,151.219588",end="-33.892023,151.216920")

print(route)        