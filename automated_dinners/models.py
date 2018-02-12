from . import db_interface as dbi

class IngredientText():
    def __init__(self, text):
        self.text = text

    def verify_text(self, db):
        """attempts to parse each line of plain text 
        recipe ingredients as an ingredient"""
        
        unittypes = dbi.get_table_list('unittype', db)
        verified_ings = ""
        verification_bool = True

        for l in self.text.split('\n'):
            if l == '':
                continue
            ing = RecipeIngredient()
            ing.parse_ing_text(l, unittypes)
            verification_text, verified = ing.display_verification()
            verified_ings += verification_text
            if not verified:
                verification_bool = False

        return verified_ings, verification_bool

    def parse(self, db):
        pass


class RecipeIngredient():
    def __init__(self, ing_dict=None, ing_text=None):
        self.attributes = ['name', 'unittypename', 'unittype', 'units']
        
        if ing_dict is not None:
            for key in self.attributes:
                self.key = ing_dict.get(key, None)

        elif ing_text is not None:
            self.ing_text = ing_text
    
    def parse_ing_text(self, text, unittype_options):
        # first remove any display_verification markings
        clean_text = text.replace('[X]', '').replace('[', '').replace(']', '')
        clean_text = clean_text.strip()

        # identify units
        # assume it's the first word

        def isfloat(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        units = text.split(' ')[0]
        if units.isdigit():
            self.units = units
        elif isfloat(units):
            self.units = units

        # identify unittype
        for u in unittype_options:
            if u['name'] in text:
                self.unittypename = u['name']
                self.unittypeid = u['id']
                break

        # identify ingredient name
        text_no_units = clean_text
        for key in ['units', 'unittypename']:
            if hasattr(self, key):
                print("removing {} '{}' from {}".format(key, getattr(self, key), clean_text))
                text_no_units = text_no_units.replace(getattr(self, key), '')
                
        self.name = text_no_units.strip()
        return

    def pretty_print(self):
        for key in self.attributes:
            print("{}: {}".format(ing_dict.get(key, 'not found')))

    def display_verification(self):
        """prints a plain text line indicating how well the ingredient was parsed
        and also returns a bool for whether the string is verified"""
        if hasattr(self, 'name') and hasattr(self, 'unittypename') and hasattr(self, 'units'):
            status = ' '
            verification_bool = True
        else:
            status = 'X'
            verification_bool = False

        return "[{:>4}] [{:>10}] [{:>14}] [{}]\n".format(getattr(self, 'units', ''), 
                                                getattr(self, 'unittypename', ''), 
                                                getattr(self, 'name', '') ,
                                                status), verification_bool





