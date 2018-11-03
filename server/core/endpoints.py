class Overpass:
    BASE = 'http://overpass-api.de/api/interpreter?data=[out:json]'
    NODE = BASE + 'node({});out;'
    WAY = BASE + 'way({});out;'