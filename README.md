# RacePace

Software Design and Development Major Project

<img src="https://img.shields.io/badge/python-3.7-brightgreen.svg?style=for-the-badge" alt="python 3.6"/>

<a href="https://discord.gg/CpwayNM"><img src="https://discordapp.com/api/guilds/426251391988662276/widget.png?style=banner2" alt="" /></a>

## Welcome
RacePace is an application that generates the best running/cycling route for the user based on a variety of factors. A route can be specified by run type, elevation, greenery and other factors such as user ratings. Coaches can use this app to track and analyse multiple participants in realtime to help runners perform at a higher level.

## Project Structure 

#### Backend:
* Our internal API written in python uses `Sanic` as an asynchronous web server.
* Clients will make requests to our API which generates a route based on given parameters using data from the Overpass API.
* Realtime tracking in the future can be made possible through the use of websockets.

#### Client:
* An android application using the Ionic framework
* Uses web technologies

## Installing the server

You must have `python 3.7+` and `pipenv`. Clone the repository and run the following command.

```
pipenv install --dev
```

To run the server navigate into the `server` folder and run `app.py`.

```
python3 app.py
```

Make sure to copy the `.env.example` file and remove the `.example` suffix so you are left with `.env`, update the key value pairs accordingly. 
