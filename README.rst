PhotoCrowd Tech Test
====================

PhotoCrowd tech test written by Tom Morledge

Time spent on the project ~9 hours

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
     :target: https://github.com/ambv/black
     :alt: Black code style


Project
-------

Unfortunantly the project is not as complete as I would of liked it to of been due to time constraints but it does furfill the brief given.

There are some tests but is no where near a full suite of tests as would be expect in a production ready system. There are tests surrounding
the core logic that generates the leaderboard.

Poetry was used as the dependancy manager for this project, you can install poetry with the following command:

    $ pip install poetry

Once installed you can install the dependencies by running:

    $ poetry install

If you don't wish to use poetry a `requirements.txt` is also provided

Currently the provided `scores.json` can be imported and parsed using a custom django command:

    $ python manage.py import_user_submissions resources/scores.json

Once the data has been imported you can run the Django application locally by running:

    $ python manage.py runserver

Once the server is running you can access the leaderboard through the UI at "http://localhost:8000/leaderboard"

You can also access the data for the leaderboard through the REST API at "http://localhost:8000/api/submissions/rankings/"

I created a Dockerfile that will setup the project for you and import `scores.json`. There is also a docker compose file `local.yml`
for running the system with a postgres database.


Tech
----

I decided to use Django as a web server as I'm very familiar with it and becuase it is also part of PhotoCrowd's tech stack.

I attempted to use django datatable packages for rendering the leaderboard table but due to the complexity of the data and the way
it is produced I ended up having to run with something custom.

I mostly followed my own style guide for the design of the of the django app and also made sure all code conforms to black, PEP8 and
mypy.

For the UI I used Django's builtin template rendering because I have a good understanding of it's workings and it very quick for
prototyping.


Future
------

Given more time I would of liked to of implemented an authentication mechanism and deployed this to Heroku. The project is setup with
the required files to be able to be deployed on Heroku but I wasn't comfortable putting it up without an authentication system in place.

I would also of liked to implement a GraphQL version of the API and flushed out the UI more to be able to display more data (individual pages
for listing/detailing competitions/users etc.)
