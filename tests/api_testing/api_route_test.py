from client import TestApiClient


client = TestApiClient()

start = "-33.878363,151.104490" #burwood
end = "-33.912466, 151.103120" #campsi
#Not working for start and end
# start = "-33.892098, 151.216802"
# end = "-33.886053, 151.218030"

#Working
# start = "-33.8776173, 151.2012087"
# end = "-33.8831174, 151.2045339"

#home to inter
# start = "-34.007263, 151.022584"
# end = "-34.009659, 151.021682"

# start = "-33.8839540, 151.2022011"
# end = "-33.8791403, 151.2011415"

route = client.get_route(start,end)

print(route)