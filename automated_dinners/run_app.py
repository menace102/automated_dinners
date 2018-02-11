import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from . import app
from .scrape_amazon import parse_ingredient_from_amazon

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

# DATABASE COMMANDS

def connect_db():
    """Connects to the specific database"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database"""
    init_db()
    print('Initialized the database.')

def dict_to_db(x):
    assert 'type' in x.keys()
    assert 'content' in x.keys()
    func_lookup = {
        'recipe': write_recipe_to_db,
        'ingredient': write_ingredient_to_db,
        'recipetype': write_recipetype_to_db,
        'unittype': write_unittype_to_db,
    }
    assert x['type'] in func_lookup.keys()
    # call the relevant db write function from the func_lookup dict
    #   passing x's contents as the arguments 
    func_lookup[x['type']](x['content'])

def stock_db():
    from .stock_db import stock
    for entry in stock:
        dict_to_db(entry)

@app.cli.command('stockdb')
def stockdb_command():
    """Initializes the database"""
    stock_db()
    print('Stocked the database chock full of goodies.')
    
def get_db():
    """Opens a new database connection if there is none yet for the current application context"""
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

# FUNCTIONS FOR WRITING TO THE DATABASE

def write_recipe_to_db(recipe_dict):
    if DEBUG: print("Writing recipe_dict: {}".format(recipe_dict))
    """Converts an Recipe stored as a dictionary to a rows in the database"""
    db = get_db()
    db.execute('insert into recipe (name, recipetypeid, instructions) values (?, ?, ?)',
            [recipe_dict['name'], 
            recipe_dict['recipetypeid'], 
            recipe_dict['instructions']
            ])

    # retreive the recipe id of the recipe we just added
    #   so we can add the ingreients to this recipe
    # TODO this hopes that there are unique recipe names. Don't assume!
    cur = db.execute('select id from recipe where name = (?)', (recipe_dict['name'],))
    recipe_id = cur.fetchall()
    assert len(recipe_id) == 1
    recipe_id = recipe_id[0][0]

    for ing in recipe_dict['ingredients']:
        db.execute('insert into recipeingmapping (recipeid, ingredientid, unittypeid, units) values (?, ?, ?, ?)',
                (recipe_id,
                ing['ingredientid'], 
                ing['unittypeid'], 
                ing['units'],
                ))
    db.commit()

def write_recipetype_to_db(recipetype):
    if DEBUG: print("Writing recipetype: {}".format(recipetype))
    """Converts a recipetype to a row in the database"""
    db = get_db()
    if 'id' in recipetype.keys():
        db.execute('insert into recipetype (id, name) values (?, ?)', (recipetype['id'], recipetype['name'],))
    else:
        db.execute('insert into recipetype (name) values (?)', (recipetype['name'],))
    db.commit()

def write_ingredient_to_db(ingredient_dict):
    if DEBUG: print("Writing ingredient_dict: {}".format(ingredient_dict))
    """Converts an Ingredient stored as a dictionary to a row in the database"""
    db = get_db()
    db.execute('insert into ingredient (name, amazonid, unittypeid, units, price, activeyn) values (?, ?, ?, ?, ?, 1)',
            (ingredient_dict['name'], 
            ingredient_dict['amazonid'], 
            ingredient_dict['unittypeid'],
            ingredient_dict['units'],
            ingredient_dict['price'],
            ))
    db.commit()

def write_unittype_to_db(unittype):
    if DEBUG: print("Writing unittype: {}".format(unittype))
    """Converts a unittype to a row in the database"""
    db = get_db()
    if 'id' in unittype.keys():
        db.execute('insert into unittype (id, name) values (?, ?)', (unittype['id'], unittype['name'],))
    else:
        db.execute('insert into unittype (name) values (?)', (unittype['name'],))
    db.commit()

# APP COMMANDS

@app.route('/')
def show_recipes():
    db = get_db()
    cur = db.execute('select id, name from recipe order by id asc')
    recipes = cur.fetchall()
    return render_template('show_recipes.html', recipes=recipes)

@app.route('/view_recipe/<recipeid>')
def view_recipe(recipeid):
    db = get_db()
    cur = db.execute("""
        select 
            recipe.name recipename, 
            recipetype.name recipetypename, 
            recipe.instructions
        from 
            recipe
            join recipetype
                on recipe.recipetypeid = recipetype.id
        where 
            recipe.id = (?)
        """, (recipeid,))
    recipe_details = cur.fetchone()

    cur = db.execute("""
        select 
            ingredient.name ingredientname,
            ingredient.amazonid,
            ingredient.price,
            sellunittype.name sellunittype,
            ingredient.units sellunits,
            recipeunittype.name recipeunittype,
            recipeingmapping.units recipeunits
        from 
            recipe
            join recipeingmapping
                on recipe.id = recipeingmapping.recipeid
            join ingredient
                on ingredient.id = recipeingmapping.ingredientid
            join unittype recipeunittype
                on recipeingmapping.unittypeid = recipeunittype.id
            join unittype sellunittype
                on recipeingmapping.unittypeid = sellunittype.id
        where 
            recipe.id = (?)
        """, (recipeid,))
    recipe_ingredients = cur.fetchall()
    return render_template('view_recipe.html', recipe_details=recipe_details, recipe_ingredients=recipe_ingredients)


# RECIPE

@app.route('/add_recipe')
def add_recipe():
    db = get_db()
    cur = db.execute('select name from recipetype order by name asc')
    recipetypes = cur.fetchall()
    recipetypes = [x[0] for x in recipetypes]
    return render_template('add_recipe.html', recipetypes=recipetypes)

@app.route('/submit_recipe', methods=['POST'])
def submit_recipe():
    recipe_dict = {}
    recipe_dict['name'] = request.form['name']
    recipe_dict['recipetypeid'] = request.form['recipetypeid']
    recipe_dict['instructions'] = request.form['instructions']
    
    recipe_dict['ingredients'] = []
    # TODO figure out how to make a dynamic html form with variable numbers of ingredients
    # for ing in request.form['ingredients']:
    #     recipe_ing_dict = {}
    #     recipe_ing_dict['ingredientid'] = ??
    #     recipe_ing_dict['unittypeid'] = ??
    #     recipe_ing_dict['units'] = ??
    #     recipe_dict['ingredients'].append(recipe_ing_dict)
    
    write_recipe_to_db(recipe_dict)
    flash('Your recipe has been added')
    return redirect(url_for('show_recipes'))

# RECIPE TYPE

@app.route('/add_recipe_type')
def add_recipetype():
    return render_template('add_recipe_type.html')

@app.route('/submit_recipetype', methods=['POST'])
def submit_recipetype():
    write_recipetype_to_db(request.form['name'])
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
    ingredient_dict = parse_ingredient_from_amazon(driver, request.form['address'])
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
    write_ingredient_to_db(ingredient_dict)
    flash('Your ingredient has been added')
    return redirect(url_for('show_recipes'))
