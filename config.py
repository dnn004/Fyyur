import os
SECRET_KEY = os.environ.get("SECRET")
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# Local:
# SQLALCHEMY_DATABASE_URI = 'postgres://postgres@localhost:5433/fyyur'

# Production:
SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") 
