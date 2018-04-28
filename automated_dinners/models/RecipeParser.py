from .RecipeIngredientLineItemParser import RecipeIngredientLineItemParser
from .StatefulAttribute import StatefulAttribute


class RecipeParser:

    def __init__(self, dict_like_input=None, unit_types=None):
        self.name = ''
        self.recipetype = ''
        self.ingredient_text_list = []
        self.instructions_text = StatefulAttribute('instructions_text')
        self.unit_types = unit_types

        if dict_like_input is not None:
            self.name = dict_like_input['name']
            self.recipetype = dict_like_input['recipetype']

            self.parse(dict_like_input['ingredients'], dict_like_input['instructions'], self.unit_types)

    # PUBLIC METHODS =================================================================================================

    def parse(self, ingredient_text, instructions_text, unit_types):
        if unit_types is None:
            print("WARNING: trying to parse with no unit types to choose from")
        self.ingredient_text_list = self._parse_ingredient_text(ingredient_text, unit_types)
        self.instructions_text.set(self._parse_instructions_text(instructions_text))

    def verified_yn(self):
        for ingredient_line in self.ingredient_text_list:
            if not ingredient_line.verified_yn():
                print("Ingredient {} failed verification".format(ingredient_line.name))
                return False

        # if got to this pint, all ingredient lines are verified
        if self.instructions_text.verified_yn():
            return True
        else:
            print("Instructions failed verification")
            return False

    def get_ingredient_verification_text(self):
        if len(self.ingredient_text_list) == 0:
            return ''

        verification_text = ''
        for ingredient_line in self.ingredient_text_list:
            verification_text += ingredient_line.verification_text()
        return verification_text

    def to_dict(self):
        if not self.verified_yn():
            print("ERROR: recipe is not verified, cannot create dict")
            return None

        return {
            'name': self.name,
            'recipetype': self.recipetype,
            'ingredients': [ing.to_dict() for ing in self.ingredient_text_list],
            'instructions': self.instructions_text.get(),
        }

    # PRIVATE METHODS ================================================================================================

    def _parse_ingredient_text(self, text, unit_types):
        return [RecipeIngredientLineItemParser(line, unit_types) for line in text.split('\n') if line.strip() != '']

    def _parse_instructions_text(self, text):
        cleaned_text = self._remove_blank_lines(text)
        return cleaned_text

    def _remove_blank_lines(self, text):
        cleaned_instructions_lines = []
        for line in text.split('\n'):
            if line.strip() != '':
                cleaned_instructions_lines.append(line)
        return "\n".join(cleaned_instructions_lines)

    def build_recipe(self):
        pass
