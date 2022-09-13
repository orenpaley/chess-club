
from tokenize import String
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, FieldList, FormField, SelectField, widgets, SelectMultipleField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from wtforms.validators import DataRequired, Email, Length
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
  name = StringField('Tag Name', validators=[DataRequired(), Length(max=50)])

class SearchGamesForm(FlaskForm):
  search = StringField('Search chess.com users', validators=[DataRequired()])

