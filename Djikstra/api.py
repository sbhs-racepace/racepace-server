import urllib.request
req = urllib.request.Request("http://overpass-api.de/api/interpreter?data=way(-33.910,151.106,-33.900,151.116);out;")
res = urllib.request.urlopen(req).read()
with open('ways.txt',"w") as f:
    print(res,file=f)
