import base64

with open("avatar.png", "rb") as imageFile:
    image_string = base64.b64encode(imageFile.read())
    print(image_string)

file = open("png_string", "wb")
file.write(image_string)
