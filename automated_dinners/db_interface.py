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


# FUNCTIONS FOR READING FROM THE DATABASE
def get_table_list(table_name, db):
    cur = db.execute('select id, name from {} order by name asc'.format(table_name))
    results = cur.fetchall()
    return results


def list_table(table_name, db):
    rows = get_table_list(table_name, db)
    names = [x['name'] for x in rows]
    return names


def get_recipe_list(db):
    cur = db.execute('select id, name from recipe order by id asc')
    return cur.fetchall()


def get_recipe_details(recipe_id, db):
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
        """, (recipe_id,))
    return cur.fetchone()


def get_recipe_ingredients(recipe_id, db):
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
        """, (recipe_id,))
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
    results = cur.fetchall()
    return results


def search_ingredient_by_name(ingredient, db):
    cur = db.execute("select id, name "
                     "from ingredient "
                     "where lower(name) like '%{}%' "
                     "order by name asc".format(ingredient.lower()))
    matching_ingredients = cur.fetchall()
    return matching_ingredients

def get_unit_type_options(db):
    cur = db.execute("select id, name  from unittype " +\
                     "union " +\
                     "select unittypeid id, altspelling name from altunittypespelling")
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
        'altunittypespelling': write_alt_unittype_spelling_to_db,
    }
    assert x['type'] in func_lookup.keys()
    # call the relevant db write function from the func_lookup dict
    #   passing x's contents as the arguments 
    func_lookup[x['type']](x['content'], db)


def write_recipe_to_db(recipe_dict, db):
    # if DEBUG: print("Writing recipe_dict: {}".format(recipe_dict))
    """Converts an Recipe stored as a dictionary to a rows in the database"""
    # if no recipetypeid, look it up from reciptype
    if 'recipetypeid' not in recipe_dict.keys():
        cur = db.execute('select id from recipetype where name = (?)', (recipe_dict['recipetype'],))
        recipetypeid = cur.fetchall()
        assert len(recipetypeid) == 1
        recipetypeid = recipetypeid[0][0]

    cur = db.execute('insert into recipe (name, recipetypeid, instructions) values (?, ?, ?)',
               [recipe_dict['name'],
                recipe_dict.get('recipetypeid', recipetypeid),
                recipe_dict['instructions']
                ])

    # retrieve the recipe id of the recipe we just added
    #   so we can add the ingredients to this recipe
    # TODO this hopes that there are unique recipe names. Don't assume!
    recipe_id = cur.lastrowid

    for ing in recipe_dict['ingredients']:
        if 'ingredientid' not in ing.keys():
            #TODO: check if ingredient name already exists
            # create a new ingredient row first
            ingredient_id = write_ingredient_to_db(ing, db)
        db.execute('insert into recipeingmapping (recipeid, ingredientid, unittypeid, units) values (?, ?, ?, ?)',
                   (recipe_id,
                    ing.get('ingredientid', ingredient_id),
                    ing['unittypeid'],
                    ing['units'],
                    ))
    db.commit()


def write_recipetype_to_db(recipetype, db):
    """Converts a recipetype to a row in the database"""
    # if DEBUG: print("Writing recipetype: {}".format(recipetype))
    if 'id' in recipetype.keys():
        db.execute('insert into recipetype (id, name) values (?, ?)', (recipetype['id'], recipetype['name'],))
    else:
        db.execute('insert into recipetype (name) values (?)', (recipetype['name'],))
    db.commit()


def write_ingredient_to_db(ingredient_dict, db):
    """Converts an Ingredient stored as a dictionary to a row in the database"""
    # if DEBUG: print("Writing ingredient_dict: {}".format(ingredient_dict))
    if 'amazonid' in ingredient_dict.keys():
        cur = db.execute('insert into ingredient (name, amazonid, unittypeid, units, price, activeyn) values (?, ?, ?, ?, ?, 1)',
                   (ingredient_dict['name'],
                    ingredient_dict.get('amazonid', None),
                    ingredient_dict['unittypeid'],
                    ingredient_dict['units'],
                    ingredient_dict.get('price', None),
                    ))
    else:
        cur = db.execute(
            'insert into ingredient (name, unittypeid, units, activeyn) values (?, ?, ?, 0)',
            (ingredient_dict['name'],
             ingredient_dict['unittypeid'],
             ingredient_dict['units'],
             ))
    db.commit()
    return cur.lastrowid


def write_unittype_to_db(unittype, db):
    """Converts a unittype to a row in the database"""
    # if DEBUG: print("Writing unittype: {}".format(unittype))
    if 'id' in unittype.keys():
        db.execute('insert into unittype (id, name) values (?, ?)', (unittype['id'], unittype['name'],))
    else:
        db.execute('insert into unittype (name) values (?)', (unittype['name'],))
    db.commit()


def write_alt_unittype_spelling_to_db(dict, db):
    """converts a alternative_unittype_spelling dict to a row in the database"""
    if 'id' in dict.keys():
        db.execute('insert into altunittypespelling (id, unittypeid, altspelling) '
                   'values (?, ?, ?)', (dict['id'], dict['unittypeid'], dict['altspelling']))
    else:
        db.execute('insert into altunittypespelling (unittypeid, altspelling) '
                   'values (?, ?)', (dict['unittypeid'], dict['altspelling']))