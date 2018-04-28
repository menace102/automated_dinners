from . import db_interface as dbi


class IngredientText:
    def __init__(self, text):
        self.text = text

    def verify_text(self, unittypes):
        """attempts to parse each line of plain text 
        recipe ingredients as an ingredient"""

        verified_ings = ""
        verification_bool = True

        for line in self.text.split('\n'):
            if line == '':
                continue
            ing = RecipeIngredient()
            ing.parse_ing_text(line, unittypes)
            verification_text, verified = ing.display_verification()
            verified_ings += verification_text
            if not verified:
                verification_bool = False

        return verified_ings, verification_bool

    def parse(self, db):
        pass


class Attribute:

    def __init__(self, name, value=None):
        self.name = name

        if value is not None:
            self.value = value
            self.verified_yn = True
        else:
            self.value = None
            self.verified_yn = False

    def set(self, value):
        # set the value if it is not None, otherwise don't do anything
        #  this allows for attempting setting of the attribute without flipping verified_yn
        if value is not None:
            self.value = value
            self.verified_yn = True

    def get(self, return_if_not_verified=None):
        if self.verified_yn:
            return self.value
        else:
            return return_if_not_verified


class RecipeIngredient:
    def __init__(self, ing_dict=None, ing_text=None):
        self.attributes = ['name', 'unittypename', 'unittype', 'units']

        self.name = Attribute('name')
        self.unittypename = Attribute('unittypename')
        self.unittypeid = Attribute('unittypeid')
        self.units = Attribute('units')

        if ing_dict is not None:
            for key in ing_dict.keys():
                # don't try to set attributes for unexpected keys in ing_dict
                if hasattr(self, key):
                    getattr(self, key).set(ing_dict[key])

        elif ing_text is not None:
            self.ing_text = ing_text

    def clean_ing_text(self, text):
        clean_text = text.lower()
        # clear validation text
        clean_text = clean_text.replace('[X]', '').replace('[', '').replace(']', '')
        clean_text = clean_text.strip()
        chars_to_replace = {
            '¼': '0.25',
            '½': '0.5',
            '¾': '0.75',
        }
        for char, replacement in chars_to_replace.items():
            clean_text = clean_text.replace(char, replacement)
        return clean_text

    def identify_units(self, text):
        def isfloat(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        # assume it's the first word
        units = text.split(' ')[0]
        if units.isdigit():
            return units
        elif isfloat(units):
            return units

    def identify_unittype(self, text, unittype_options):
        for u in unittype_options:
            if u['name'] in text or u['name']+'s' in text:
                return u['name'], u['id']

        # if no unit type is found, default to count
        id_for_count_unittype = [u['id'] for u in unittype_options if u['name'] == 'count'][0]
        return 'count', id_for_count_unittype

    def parse_ing_text(self, text, unittype_options):
        # first remove any display_verification markings
        clean_text = self.clean_ing_text(text)

        self.units.set(self.identify_units(clean_text))
        parsed_unittypename, parsed_unittypeid = self.identify_unittype(clean_text, unittype_options)
        self.unittypename.set(parsed_unittypename)
        self.unittypeid.set(parsed_unittypeid)

        # identify ingredient name by removing the unit and unittype
        #   including checking for remaining 's's from unittype plurals
        text_no_units = clean_text.replace(self.units.get(return_if_not_verified=''), '')\
            .replace(self.unittypename.get(return_if_not_verified=''), '')\
            .replace(' s ', ' ')

        self.name.set(text_no_units.strip())
        return

    def pretty_print(self):
        for key in self.attributes:
            print("{}: {}".format(getattr(self, key, 'not found')))

    def display_verification(self):
        """prints a plain text line indicating how well the ingredient was parsed
        and also returns a bool for whether the string is verified"""
        if self.name.verified_yn and self.unittypename.verified_yn and self.units.verified_yn:
            status = 'X'
            verification_bool = True
        else:
            status = ' '
            verification_bool = False

        return "[{}] [{:>4}] [{:>10}] [{:>14}]\n".format(status,
                                                         self.units.get(return_if_not_verified=''),
                                                         self.unittypename.get(return_if_not_verified=''),
                                                         self.name.get(return_if_not_verified=''),
                                                         ), verification_bool
