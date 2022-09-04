
from tokenize import String
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, FieldList, FormField, SelectField
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

  pgn = TextAreaField('Copy your PGN text here', validators=[DataRequired()])

class PostGameExtractedForm(FlaskForm):
  "form for user to post a chess game"

  event = StringField('Event Name (Optional)')
  white = StringField('White Player Name')
  black = StringField('Black Player Name')
  result = IntegerField()

class TagForm(FlaskForm):
  name = StringField('Tag Name', validators=[DataRequired(), Length(max=50)])

class TagsGameForm(FlaskForm):
  tag_id = SelectField(u'Tag', coerce=int)

def add_form_tag(request, id):
  tag = Tag.query.get(id)
  form = TagsGameForm(request.POST, obj=tag)
  form.tag_id.choices = [(t.id, t.name) for t in Tag.query.order_by('name')]



