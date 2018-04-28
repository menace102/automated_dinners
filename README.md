# automated_dinners

## set up instructions

### Set up environment

Install miniconda: https://conda.io/miniconda.html

Create an environment: `conda create -n auto_dinners python=3.5`

Activate the environment: `source activate auto_dinners`

Install the dependencies: `pip install -e .`

### Running the application

Set flask environmental variable to enable flask cli

`export FLASK_APP=path/leading/to/run_app.py`

Optional: turn on debug mode. This makes code changes to effect without having to restart the application.

`export FLASK_DEBUG=1`

Alternatively, if you have an `instance/config.sh` set up, run `source instance/config.sh`. 

Command to initialize the database: `flask initdb`

Command to stock the database if it is empty: `flask stockdb`

Run the website! `flask run`

### Querying the Database on the command line

`sqlite3 automated_dinners/automated_dinners.db`

`.mode column`

[sqlite3 reference](https://www.sqlite.org/cli.html)
