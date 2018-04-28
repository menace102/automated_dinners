class StatefulAttribute:
    """
    Stores a name and value and a state variable to track whether or not the value has been verified
    aka successfully parsed, successfully verified with the database, or successfully verified with amazon
    """

    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def verified_yn(self):
        if self.value is None:
            return False
        # elif type(self.value) == list:
        #     if len(self.value) == 0:
        #         # return False if self.value is an empty list
        #         return False
        #     for item in self.value:
        #         if type(item) == StatefulAttribute:
        #             if not item.verified_yn():
        #                 # return False if self.value is a list containing more StatefulAttributes,
        #                 #   any of which are not verified
        #                 return False
        #         else:
        #             # return True id self.value is a list that holds things other than StatefulAttributes
        #             return True
        #     # return True if self.value is a list containing more StatefulAttributes, all of which are verified
        #     return True
        else:
            return True

    def set(self, value):
        # set the value if it is not None, otherwise don't do anything
        #  this allows for attempting setting of the attribute without flipping verified_yn
        if value is not None:
            self.value = value

    def get(self, return_if_not_verified=None, override=False):
        if self.verified_yn() or override:
            return self.value
        else:
            return return_if_not_verified
