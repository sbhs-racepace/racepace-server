class Overpass:
    BASE = 'http://overpass-api.de/api/interpreter?data=[out:json];'
    NODE = BASE + 'node({});out;'
    WAY = BASE + 'way({});out;'

class Color:
    green = 0x2ecc71
    red = 0xe74c3c
    orange = 0xe67e22