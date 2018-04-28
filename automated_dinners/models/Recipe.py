class Recipe:

    def __init__(self, input):
        self.name = ''
        self.ingredients = [] # list of tuples, each tuple contains
        self.instructions = []  # list of strings, one string per instruction step


    def parse_json(self, input):
        pass


    def parse_html(self, input):
        pass


class Ingredient:

    def __init__(self, input):
        self.name = ''
        self.ingredients = []
        self.instructions = []

    def parse_json(self, input):
        pass

    def parse_html(self, input):
        pass