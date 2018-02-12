"""find recipe
copy and paste ingredients and instructions into box
parse ingredients
    search db for ingredient
    if we dont have it:
        ask for amazon entry (starting with opening amazon with search?)
        add ingredient entry
    encode recipe ingredients
encode instructions
"""

ingredients = """
2 count Sweet Potato
1 count Shallot
0.25 ounces Rosemary
12 ounces Chicken Breasts
5 teaspoon Balsamic Vinegar
0.5 ounces Fig Jam
1 count Chicken Stock Concentrate
1 tablespoon Butter
"""


instructions = """
1. Preheat oven to 425 degrees. 
2. Cut sweet potatoes into 1/2-inch cubes. Toss on a baking sheet with a drizzle of olive oil and a pinch of salt and pepper. Roast in oven until tender and crisped, 20-25 minutes.
3. Heat a drizzle of olive oil in a large pan over medium-high heat. Pat chicken dry with a paper towel and season all over with salt and pepper. Cook in pan until no longer pink in center, 5-7 minutes per side. Remove from pan and set aside to rest.
4. Halve, peel, and mince shallot. Strip enough and chop enough rosemary leaves from stems to give you 1 tsp.
5. Lower heat under pan to medium. Add shallot, chopped rosemary, and a drizzle of olive oil. Cook, tossing, until softened, 2-3 minutes. 
6. Stir in Colavita balsamic vinegar and half the fig jam. Simmer until syrupy, about 1 minute. 
7. Stir in 1/2 cup water and stock concentrate. Let reduce until saucy, about 3 minutes. 
8. Remove from heat. Stir in 1 Tbsp butter. Season with salt and pepper.
9. Thinly slice chicken, then divide between plates along with sweet potatoes. Drizzle chicken with sauce. 
"""

import os
from automated_dinners import db_interface as dbi
db_path = os.path.join('automated_dinners', 'automated_dinners.db')
db = dbi.connect_db(db_path)

# ing_dict = {
#     'type': 'ingredient',
#     'name': 'carrots', 
#     'amazonid': 'https://www.amazon.com/produce-aisle-mburring-Carrots-lb/dp/B000NSFQH6/ref=sr_1_4_f_f_it?s=amazonfresh&ie=UTF8', 
#     'unittypeid': 2,
#     'units': 2,
#     'price': 1.79,
# }

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

def parse_ingredient(text, unittype_options):
    ing_dict = {
        'type': 'ingredient',
    }

    # identify units
    # assume it's the first word
    units = text.split(' ')[0]
    if units.isdigit():
        ing_dict['units'] = int(units)
    elif float(units):
        ing_dict['units'] = float(units)


    # identify unittype
    for u in unittype_options:
        if u['name'] in text:
            ing_dict['unittypename'] = u['name']
            ing_dict['unittypeid'] = u['id']
            break

    # identify ingredient name
    text_no_units = text.replace(units, '').replace(u['name'], '')
    ing_dict['name'] = text_no_units
    
    return ing_dict

def pretty_print_ing_dict(ing_dict):
    print("name: {}".format(ing_dict.get('name', 'not found')))
    print("unittypename: {}".format(ing_dict.get('unittypename', 'not found')))
    print("unittypeid: {}".format(ing_dict.get('unittypeid', 'not found')))
    print("units: {}".format(ing_dict.get('units', 'not found')))

def parse_ingredient_text(ingredient_string, db):
    """turn plain text recipe into recipe dict, entering 
    ingredients if they dont already exist"""
    unittypes = dbi.get_table_list('unittype', db)
    print([u['name'] for u in unittypes])

    ing_list = []
    for l in ingredient_string.split('\n'):
        if l == '':
            continue
        print('\n'+l)
        ing_dict = parse_ingredient(l, unittypes)
        pretty_print_ing_dict(ing_dict)
        ing_list.append(ing_dict)

    return ing_list

def parse_recipe_from_form(form, db):
    recipe_dict = {}
    recipe_dict['name'] = form['name']
    recipe_dict['recipetype'] = form['recipetype']
    recipe_dict['ingredients'] = parse_ingredient_text(form['ingredients'], db)
    recipe_dict['instructions'] = form['instructions']
    return recipe_dict

