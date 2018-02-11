stock = [
	# UNIT TYPES
	{
		'type': 'unittype',
		'content': {
			'id': 1,
			'name': 'count'
		}
	},
	{
		'type': 'unittype',
		'content': {
			'id': 2,
			'name': 'pounds'
		}
	},
	{
		'type': 'unittype',
		'content': {
			'id': 3,
			'name': 'ounces'
		}
	},
	{
		'type': 'unittype',
		'content': {
			'id': 4,
			'name': 'grams'
		}
	},
	{
		'type': 'unittype',
		'content': {
			'id': 5,
			'name': 'liters'
		}
	},
	{
		'type': 'unittype',
		'content': {
			'id': 6,
			'name': 'teaspoon'
		}
	},
	{
		'type': 'unittype',
		'content': {
			'id': 7,
			'name': 'tablespoon'
		}
	},
	{
		'type': 'unittype',
		'content': {
			'id': 8,
			'name': 'cup'
		}
	},
	# RECIPE TYPES
	{
		'type': 'recipetype',
		'content': {
			'id': 1,
			'name': 'main course'
		}
	},
	{
		'type': 'recipetype',
		'content': {
			'id': 2,
			'name': 'vegetable'
		}
	},
	{
		'type': 'recipetype',
		'content': {
			'id': 3,
			'name': 'side'
		}
	},
	{
		'type': 'recipetype',
		'content': {
			'id': 4,
			'name': 'dessert'
		}
	},
	# INGREDIENTS
	{
		'type': 'ingredient',
		'content': {
			'name': 'carrots', 
            'amazonid': 'https://www.amazon.com/produce-aisle-mburring-Carrots-lb/dp/B000NSFQH6/ref=sr_1_4_f_f_it?s=amazonfresh&ie=UTF8', 
            'unittypeid': 2,
            'units': 2,
            'price': 1.79,
		}
	},
	{
		'type': 'ingredient',
		'content': {
			'name': 'cinnamon', 
            'amazonid': 'https://www.amazon.com/McCormick-Ground-Cinnamon-1-oz/dp/B0005XNEUK/ref=sr_1_5_f_f_it?s=amazonfresh&ie=UTF8', 
            'unittypeid': 3,
            'units': 1,
            'price': 1.99,
		}
	},
	# RECIPES
	{
		'type': 'recipe',
		'content': {
			'name': 'Cooked Carrots', 
            'recipetypeid': 1, 
            'instructions': 'Cook the carrots with cinnamon until soft.',
            'ingredients': [
	            {
	            	'ingredientid': 1, 
	                'unittypeid': 1, 
	                'units': 4,
               },
               {
	            	'ingredientid': 2, 
	                'unittypeid': 6, 
	                'units': 1,
               },
            ]
		}
	}
]