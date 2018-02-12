from flask import Flask

app = Flask(__name__)
from . import run_app
from . import scrape_amazon
from . import db_interface
