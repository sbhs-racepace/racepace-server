from client import TestApiClient

client = TestApiClient()
client.register_user(email="gahugga@gmail.com", password="bobby")
user = client.login(email="gahugga@gmail.com", password="bobby")


client.create_group()
