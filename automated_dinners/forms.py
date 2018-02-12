from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField,
   SelectField

from wtforms import validators, ValidationError

class RecipeForm(Form):
   name = TextField("Recipe Name",[validators.Required("Please enter your name.")])
   
   Age = IntegerField("age")
   language = SelectField('Languages', choices = [('cpp', 'C++'), 
      ('py', 'Python')])
   submit = SubmitField("Send")