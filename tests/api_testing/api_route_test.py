from client import TestApiClient


client = TestApiClient()

start = "-33.8776173,151.2012087"
end = "-33.8831174,151.2045339"

route = client.get_route(start,end)

print(route)