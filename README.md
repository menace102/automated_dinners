# automated_dinners

## set up instructions

### Set up environment

Install miniconda
https://conda.io/miniconda.html

Create an environment

`conda create -n auto_dinners python=3.5`

Activate the environment

`source activate auto_dinners`

<Insert command for installing requirements.txt or setup.py>

### Running the application

Set flask environmental variable to enable flask cli

`export FLASK_APP = path/leading/to/automated_dinner.py`

Optional: turn on debug mode. This makes code changes to effect without having to restart the application.

`export FLASK_DEBUG=1`

Command to initialize the database

`flask initdb`

Command to stock the database if it is empty:

`flask stockdb`

Run the website!

`flask run`
