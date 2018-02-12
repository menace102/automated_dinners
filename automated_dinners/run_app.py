import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from . import app
from . import db_interface as dbi
from .models import *
from . import scrape_amazon as az
from . import parsers

import pdb
DEBUG = 1

# app = Flask(__name__) # create the application instance
# app.config.from_object(__name__) # load config from this file, flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'automated_dinners.db'),
    SECRET_KEY='development key and some randomness SNAKESS!',
    USERNAME='admin',
    PASSWORD='notthedefaultpassword'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


# CLI COMMANDS ##########################################

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database"""
    db = get_db()
    dbi.init_db(db)
    print('Initialized the database.')

@app.cli.command('stockdb')
def stockdb_command():
    """Initializes the database"""
    db = get_db()
    dbi.stock_db(db)
    print('Stocked the database chock full of goodies.')

@app.cli.command('dbcli')
def dbcli():
    pass

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# DATABASE COMMANDS ##########################################

def get_db():
    """Opens a new database connection if there is none yet for the current application context"""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = dbi.connect_db(app.config['DATABASE'])
    return g.sqlite_db

def init_db(db):
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

# ROUTING FUNCTIONS ##########################################

# RECIPE

@app.route('/')
def show_recipes():
    db = get_db()
    recipes = dbi.get_recipe_list(db)
    return render_template('show_recipes.html', recipes=recipes)

@app.route('/view_recipe/<recipeid>')
def view_recipe(recipeid):
    db = get_db()
    recipe_details = dbi.get_recipe_details(recipeid, db)
    recipe_ingredients = dbi.get_recipe_ingredients(recipeid, db)
    return render_template('view_recipe.html', recipe_details=recipe_details, recipe_ingredients=recipe_ingredients)

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    db = get_db()
    recipetypes = dbi.list_recipetypes(db)
    if request.method == 'GET':
        return render_template('parse_recipe.html', recipe_dict={}, recipetypes=recipetypes)
    elif request.method == 'POST':
        parsed_recipe = request.form.copy()
        parsed_recipe['ingredients'], verified = IngredientText(parsed_recipe['ingredients']).verify_text(db)
        recipetypes = dbi.list_recipetypes(db)
        if verified:
            flash('Your recipe is verified and ready for storage, but double check for parsing errors')
            return render_template('add_recipe.html', recipe_dict=parsed_recipe, recipetypes=recipetypes)
        else:
            flash('Your recipe has errors')
            return render_template('parse_recipe.html', recipe_dict=parsed_recipe, recipetypes=recipetypes)

@app.route('/submit_recipe', methods=['POST'])
def submit_recipe():
    # recipe_dict = {}
    # recipe_dict['name'] = request.form['name']
    # recipe_dict['recipetypeid'] = request.form['recipetypeid']
    # recipe_dict['instructions'] = request.form['instructions']
    
    # recipe_dict['ingredients'] = []
    # # TODO figure out how to make a dynamic html form with variable numbers of ingredients
    # # for ing in request.form['ingredients']:
    # #     recipe_ing_dict = {}
    # #     recipe_ing_dict['ingredientid'] = ??
    # #     recipe_ing_dict['unittypeid'] = ??
    # #     recipe_ing_dict['units'] = ??
    # #     recipe_dict['ingredients'].append(recipe_ing_dict)
    
    # db = get_db()
    # dbi.write_recipe_to_db(recipe_dict, db)
    flash('Your recipe for {} has [not actually] been added'.format(request.form['name']))
    return redirect(url_for('show_recipes'))

# RECIPE TYPE

@app.route('/add_recipe_type')
def add_recipetype():
    return render_template('add_recipe_type.html')

@app.route('/submit_recipetype', methods=['POST'])
def submit_recipetype():
    db = get_db()
    dbi.write_recipetype_to_db(request.form['name'], db)
    flash('Your recipetype has been added')
    return redirect(url_for('show_recipes'))

# INGREDIENT

@app.route('/add_ingredient')
def add_ingredient_noargs():
    return render_template('add_ingredient.html', ingredient_dict={})

@app.route('/add_ingredient/<ingredient_dict>')
def add_ingredient(ingredient_dict):
    return render_template('add_ingredient.html', ingredient_dict=ingredient_dict)

@app.route('/parse_ingredient', methods=['POST'])
def parse_ingredient():
    print("got into parse_ingredient")
    driver = webdriver.Chrome()
    ingredient_dict = az.parse_ingredient_from_amazon(driver, request.form['address'])
    driver.close()
    print(ingredient_dict)
    if len(ingredient_dict) == 0:
        flash("Error parsing Amazon page. Check your url: {}".format(request.form['address']))
    else:
        flash("Here's what I found on Amazon")
    return render_template('add_ingredient.html', ingredient_dict=ingredient_dict)

@app.route('/submit_ingredient', methods=['POST'])
def submit_ingredient():
    ingredient_dict = {}
    ingredient_dict['name'] = request.form['name']
    ingredient_dict['amazonid'] = request.form['amazonid']
    ingredient_dict['unittypeid'] = request.form['unittypeid']
    ingredient_dict['units'] = request.form['units']
    ingredient_dict['price'] = request.form['price']
    db = get_db()
    dbi.write_ingredient_to_db(ingredient_dict, db)
    flash('Your ingredient has been added')
    return redirect(url_for('show_recipes'))
