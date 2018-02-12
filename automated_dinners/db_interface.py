import os
import sqlite3
from flask import Flask, g
import pdb

def connect_db(path):
    """Connects to the specific database"""
    rv = sqlite3.connect(path)
    rv.row_factory = sqlite3.Row
    return rv

def stock_db(db):
    from .stock_db import stock
    for entry in stock:
        dict_to_db(entry, db)

# FUNCIONS FOR READING FROM THE DATABASE
def get_table_list(tablename, db):
    cur = db.execute('select id, name from {} order by name asc'.format(tablename))
    recipetypes = cur.fetchall()
    return recipetypes

def list_table(tablename, db):
    rows = get_table_list(tablename, db)
    names = [x['name'] for x in rows]
    return names

def get_recipe_list(db):
    cur = db.execute('select id, name from recipe order by id asc')
    return cur.fetchall()

def get_recipe_details(recipeid, db):
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
    return cur.fetchone()

def get_recipe_ingredients(recipeid, db):
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
    return cur.fetchall()

def get_recipetype_list(db):
    cur = db.execute('select id, name from recipetype order by name asc')
    recipetypes = cur.fetchall()
    return recipetypes

def list_recipetypes(db):
    recipetype_rows = get_recipetype_list(db)
    recipetypes = [x['name'] for x in recipetype_rows]
    return recipetypes

def get_ingredient_list(db):
    cur = db.execute('select id, name from ingredient order by name asc')
    recipetypes = cur.fetchall()
    return recipetypes

def search_ingredient_by_name(ingredient, db):
    cur = db.execute('select id, name from ingredient where lower(name) like '%{}%' order by name asc'.format(ingredient))
    matching_ingredients = cur.fetchall()
    return matching_ingredients

# FUNCTIONS FOR WRITING TO THE DATABASE

def dict_to_db(x, db):
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
    func_lookup[x['type']](x['content'], db)

def write_recipe_to_db(recipe_dict, db):
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

def write_recipetype_to_db(recipetype, db):
    """Converts a recipetype to a row in the database"""
    if DEBUG: print("Writing recipetype: {}".format(recipetype))
    if 'id' in recipetype.keys():
        db.execute('insert into recipetype (id, name) values (?, ?)', (recipetype['id'], recipetype['name'],))
    else:
        db.execute('insert into recipetype (name) values (?)', (recipetype['name'],))
    db.commit()

def write_ingredient_to_db(ingredient_dict, db):
    """Converts an Ingredient stored as a dictionary to a row in the database"""
    if DEBUG: print("Writing ingredient_dict: {}".format(ingredient_dict))
    db.execute('insert into ingredient (name, amazonid, unittypeid, units, price, activeyn) values (?, ?, ?, ?, ?, 1)',
            (ingredient_dict['name'], 
            ingredient_dict.get('amazonid', None), 
            ingredient_dict['unittypeid'],
            ingredient_dict['units'],
            ingredient_dict.get('price', None),
            ))
    db.commit()

def write_unittype_to_db(unittype, db):
    """Converts a unittype to a row in the database"""
    if DEBUG: print("Writing unittype: {}".format(unittype))
    if 'id' in unittype.keys():
        db.execute('insert into unittype (id, name) values (?, ?)', (unittype['id'], unittype['name'],))
    else:
        db.execute('insert into unittype (name) values (?)', (unittype['name'],))
    db.commit()


