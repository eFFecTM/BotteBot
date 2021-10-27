# Botte Bot
Doc is outdated, needs overhaul!

## Features
This repository is used to create a Slack bot which can perform various things:
* Insult people
* Check the current weather at a given location
* Define a word you mentioned in a conversation
* Translate sentences
* ... More coming soon!

## Get started (incomplete, does not consider database)
* Install python and pip3.
* Install the requirements.txt file (pip3 install -r requirements.txt).
* Get the necessary API keys and add them to a _init.ini_ file which has to be created inside the config folder.

## To do
* Use user ids instead of nicknames for persisting data.
* Expand food order poll system to a generic poll which users can create (replaced of Polly).
* Further improve visualisation of polls and their results based on feedback.
* Automatic setup of database schema (programatically)
* polls on tuesday instead of wednesday
* bug: last message is modified to food order
* store user ids to display users
* bring back food order lists view, but only show first 5 or 10 with extra info
* close poll after wednesday 16:00
* separate poll for voting restaurant
* separate poll after food wednesday evening to vote / give rating
* bot should reply in thread when it was triggered from an existing thread (e.g. insult is posted separately now)

## Authors
* Jan De Laet
* Thomas Janssen
* Liam Oorts

This project is part of the iMagineLab codehub. See [imaginelab.club]().
