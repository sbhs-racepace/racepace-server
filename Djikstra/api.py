import urllib.request
LOCATION = "-33.910,151.106,-33.900,151.116"
req = urllib.request.Request(f"http://overpass-api.de/api/interpreter?data=way({LOCATION});out;")
res = str(urllib.request.urlopen(req).read(),"ascii")
with open('ways.txt',"w") as f:
    print(res,file=f)

req = urllib.request.Request(f"http://overpass-api.de/api/interpreter?data=node({LOCATION});out;")
res = str(urllib.request.urlopen(req).read(),"ascii")
with open('nodes.txt',"w") as f:
    print(res,file=f)
