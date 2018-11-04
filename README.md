# RacePace
Software Design and Development Major Project

<img src="https://img.shields.io/badge/python-3.7-brightgreen.svg?style=for-the-badge" alt="python 3.6" />

## Summary
An app that generates the best running/cycling route for the user based on a variety of factors. A route can be specified by run type, elevation, greenery and other factors such as user ratings. Coaches can use this app to track and analyse multiple participants in realtime to help runners perform at a higher level.

## Project Structure 

#### Backend:
* Our internal API written in python uses `Sanic` as an asynchronous web server.
* Clients will make requests to our API which generates a route based on given parameters using data from the Overpass API.
* Realtime tracking in the future can be made possible through the use of websockets.

#### Android Application:
Ionic framework
