# community-slackbot

## Setup
Ensure you have a slack app created with the necessary permissions and correct request urls (see server.py for details on the required url for each type of slack request).

## Development

To run in development copy the .env.example to .env and fill all the environment variables in accordingly.
To run the flask development server run the ```wsgi.py``` file.

To install dependencies run ```pip3 install -r requirements.txt``` in the root folder.

## Database
To run migrations and setup your own database with all the tables, first ensure you have run the command ```flask db init``` and 
ensure it creates a migrations folder in the root of your project. Then run the command ```flask db migrate``` to generate migrations 
files for any table changes then run ```flask db upgrade``` to apply the migrations to your database.
