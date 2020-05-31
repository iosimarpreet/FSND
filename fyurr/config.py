import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{os.env["FYURR_DB_USER"]}:{os.env["FYURR_DB_PASSWORD"]}@{os.env["FYURR_DB_HOST"]}:5432/{os.env["FYURR_DB_NAME"]}'
