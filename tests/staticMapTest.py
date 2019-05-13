from staticmap import StaticMap, Line
import base64
from io import BytesIO
m = StaticMap(50,50)
route = [[151.103812,-33.911057],[151.107460,-33.90315]]
for pts in zip(route[:-1],route[1:]):
    print(pts)
    line = Line(pts,"blue", 2)
    m.add_line(line)
image = m.render()
buffer = BytesIO()
image.save(buffer, format="PNG")
print(base64.b64encode(buffer.getvalue()))

##m = StaticMap(200, 200, 80)
##
##coordinates = [[12.422, 45.427], [13.749, 44.885]]
##line_outline = Line(coordinates, 'white', 6)
##line = Line(coordinates, '#D2322D', 4)
##
##m.add_line(line_outline)
##m.add_line(line)
##
##image = m.render()
##image.save('ferry.png')
