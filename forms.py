
import email
from tokenize import String
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, FieldList, FormField, SelectField, widgets, SelectMultipleField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from wtforms.validators import DataRequired, Email, Length, NumberRange
from models import Tag

class RegisterForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_url = StringField('(Optional) Image URL')
   

    # first_name = StringField('(Optional) first name')
    # last_name = StringField('(Optional) last name')
    # location = StringField('(Optional) location')
    # bio = StringField('(Optional) tell us about yourself')

class LoginForm(FlaskForm):
  "form to authenticate login"

  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[Length(min=6)])

class PostGameForm(FlaskForm):
  "form for user to post a chess game"
  title = StringField('Title', validators=[DataRequired()])
  pgn = TextAreaField('Copy your PGN text here', validators=[DataRequired()])

class TagForm(FlaskForm):
  """form to add tags to global tags list"""
  name = StringField('Tag Name', validators=[DataRequired(), Length(max=50)])

class SearchGamesForm(FlaskForm):
  """Form to search chesscom users"""
  username = StringField('chess.com username', validators=[DataRequired()])
  year = IntegerField(validators=[NumberRange(min=1990,max=2022)])
  month = IntegerField(validators=[NumberRange(min=1, max=12)])
  offset = IntegerField(validators=[NumberRange(min=0, max=9999)])
  limit = IntegerField(validators=[NumberRange(min=1, max=50)])

class UserProfileForm(FlaskForm):
  """class to edit user profile info"""
  username = StringField('Username', validators=[DataRequired(), Length(max=50)])
  first_name = StringField('First Name', validators=[Length(max=50)])
  last_name = StringField('Last Name', validators=[Length(max=50)])
  email = StringField('Email', validators=[Length(max=100), Email()])
  image_url = StringField('(Optional) Image URL')
  location = StringField('Location', validators=[Length(max=50)])
  bio = TextAreaField('Bio')
   
  


