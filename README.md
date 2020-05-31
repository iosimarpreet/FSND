# Fyyur


## As Submitted

GitHub Link for the submission: [Link](https://github.com/iosimarpreet/FSND/tree/projects/fyurr_submission)

### Dev Setup

1. Clone the repository & Navigate to the Fyurr App

`git clone https://github.com/iosimarpreet/FSND.git simarpreet_FSND`

2. Then, checkout the Fyurr App submission branch and cd into the project dir.

`git checkout -b projects/fyurr_submission`
`cd fyurr`

3. Setup the following environment variables

* `FYURR_DB_USER`
* `FYURR_DB_PASSWORD`
* `FYURR_DB_HOST`
* `FYURR_DB_NAME`

These are to connect to the db in `config.py`.

4. Create & activate a virtual environment

`python -m venv env`
`source env/bin/activate`

5. Install all of the python dependencies

`pip install -r requirements.txt`

6. Start the server

`python app.py`

### Database Migration

In `app.py` uncomment `app.run()` and add `manager.run()`. Then, from the command-line you can run 

`python3 app.py db init`

if this is the first time you are running the app.

Otherwise to doa  migration, you can do:

`python3 app.py db migrate`
`python3 app.py db upgrade`

Once the migration is done, comment out / remove `manager.run()` from `app.py` and uncomment / add back in `app.run()`. You should see all Database changes present now and the app should run.