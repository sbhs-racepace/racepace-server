from client import TestApiClient


client = TestApiClient()

start = "-33.878363,151.104490" #burwood
end = "-33.912466, 151.103120" #campsi

route = client.get_route(start,end)

print(route)