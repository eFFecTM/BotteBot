# Botte Bot - RUDE-i

## Features
This repository is used to create a Slack bot which can perform various things:
* Insult people
* Check the current weather at a given location
* Define a word you mentioned in a conversation
* Translate sentences
* ... More coming soon!

## Get started
### Installing
* Install python and pip3 for your OS.
* Install the requirements.txt file: `pip3 install -r requirements.txt`
* Get the necessary API keys for services (e.g. Google API key), and add them to a _init.ini_ file which has to be created inside the _config_ folder.
* Request the SQLite database file _imaginelab.db_ from one of the authors, and add it to the _data_ folder.

### Debugging
* When developing modal, install a local tunnel and run the following command: \
`lt -h http://loca.lt -p 3000 -s bottebot`

* When debugging the database, use the 'DB Browser for SQLite' program to view and/or edit the database file.

## To do
### Features
* Replace modal text for ordering with table
* separate poll for voting restaurant
* Use user ids instead of nicknames for persisting data.
* Display full username instead of nickname when ordering food.
* Automatic setup of database schema (programmatically)
* bot should reply in thread when it was triggered from an existing thread (e.g. insult is posted separately now)
* View list of bugs

### Known bugs
* Update label of food orders to display number of eaters and votes correctly
* Check issues with saving orders
* _See also the database of bugs!_

## Authors
* Jan De Laet
* Thomas Janssen
* Liam Oorts

This project is part of the iMagineLab codehub. See [imaginelab.club]().
