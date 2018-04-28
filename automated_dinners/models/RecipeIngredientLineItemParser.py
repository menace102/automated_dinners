from fractions import Fraction
from .StatefulAttribute import StatefulAttribute


class RecipeIngredientLineItemParser:

    def __init__(self, text, unittype_options):
        self.attributes = ['name', 'unittypename', 'unittype', 'units']

        self.name = StatefulAttribute('name')
        self.unittypename = StatefulAttribute('unittypename')
        self.unittypeid = StatefulAttribute('unittypeid')
        self.units = StatefulAttribute('units')
        self.unittype_options = unittype_options

        self.parse(text)

    # PUBLIC METHODS =================================================================================================

    def parse(self, text):
        self._parse_from_text(text)

    def verified_yn(self):
        return self.name.verified_yn() and self.unittypename.verified_yn() and self.units.verified_yn()

    def verification_text(self):
        """prints a plain text line indicating how well the ingredient was parsed"""
        status = ' '
        if self.verified_yn():
            status = 'X'

        return "[{}] [{:>4}] [{:<10}] [{:<25}]\n".format(status,
                                                         self.units.get(return_if_not_verified=''),
                                                         self.unittypename.get(return_if_not_verified=''),
                                                         self.name.get(return_if_not_verified=''),
                                                         )

    def to_dict(self):
        if not self.verified_yn():
            print("ERROR: ingredient is not verified, cannot create dict")
            return None

        return {
            'name': self.name.get(),
            'unittypeid': self.unittypeid.get(),
            'units': self.units.get(),
        }

    # PRIVATE METHODS ================================================================================================

    def _parse_from_text(self, text):
        clean_text = self._clean_text(text)

        units, remaining_text = self._identify_units(clean_text)
        try:
            if float(units) > 0:
                self.units.set(units)
        except:
            pass

        unittype_dict, remaining_text = self._identify_unittype(remaining_text, self.unittype_options)
        self.unittypename.set(unittype_dict['name'])
        self.unittypeid.set(unittype_dict['id'])

        self.name.set(remaining_text.strip())

    def _clean_text(self, text):
        clean_text = text.lower()
        clean_text = clean_text.strip()

        clean_text = self._remove_verification_chars(clean_text)
        print(clean_text)
        clean_text = self._replace_non_ascii_characters(clean_text)
        clean_text = self._consolidate_leading_numbers(clean_text)
        return clean_text

    def _remove_verification_chars(self, text):
        return text.replace('[x]', '').replace('[X]', '').replace('[', '').replace(']', '').strip()

    def _replace_non_ascii_characters(self, text):
        chars_to_replace = {
            '¼': '0.25',
            '½': '0.5',
            '¾': '0.75',
        }
        for char, replacement in chars_to_replace.items():
            # spaces before the replacements are necessary
            #  in case of things like 1¼ cup, which would otherwise become 10.25
            text = text.replace(char, ' '+replacement)
        return text

    def _consolidate_leading_numbers(self, text):
        """
        Start at the begining of the text and add up all consecutive numbers, including fractions
        for example, input = '1 1/2 cup flour' output = '1.5 cup flour'
        """
        def to_number(value):
            try:
                return float(value)
            except ValueError:
                try:
                    return float(Fraction(value))
                except ValueError:
                    return None

        total = float(0.0)
        text_with_new_number = text
        for word in text.split(' '):
            word = word.strip()
            if word == '':
                continue
            number = to_number(word)
            if number is not None:
                total = float(number)
                # now that we've added it, remove this number- we'll add the total back on at the end
                text_with_new_number = text_with_new_number.replace(word, '')
            else:
                break
        return str(round(total, 2)) + text_with_new_number

    def _identify_units(self, text):
        """
        find the units from the text, though only if it's the first thing in the text
        :param text: text in which to identify units
        :return: (1) the units (if not found, None)
                 (2) the text remaining after the units
        """
        def isfloat(value):
            try:
                float(value)
                return True
            except ValueError:
                return False

        tokens = text.split(' ')
        suspected_units = tokens[0]  # assume it's the first word
        if suspected_units.isdigit() or isfloat(suspected_units):
            units = suspected_units
            if len(tokens) > 1:
                remaining_text = " ".join(tokens[1:])
            else:
                remaining_text = ''
            return units, remaining_text
        else:
            return None, text

    def _identify_unittype(self, text, unittype_options):
        """
        Look for any matches of unit type names in the tet and return the first match
        :param text: the text in which to identify the unit type
        :param unittype_options: a list of sqlite Row objects (dict-like) with id and name columns
        :return: (1) a unittype_dict describing the unittype with keys name and id
                    (if not found, default to the 'count' unittype)
                 (2) the remaining text after extracting unittype
        """
        default_unittype = 'count'

        unittype_options_dict = {}
        for entry in unittype_options:
            unittype_options_dict[entry['name']] = entry['id']

        # set the return_dict to the default values in case no unit type is found
        return_dict = {
            'name': default_unittype,
            'id': unittype_options_dict[default_unittype],
        }

        for token in text.split(' '):
            if token in unittype_options_dict.keys():
                return_dict['name'] = token
                return_dict['id'] = unittype_options_dict[token]
                remaining_text = text.replace(token, '')
                return return_dict, remaining_text

        return return_dict, text

