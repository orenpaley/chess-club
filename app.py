
import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import PostGameExtractedForm, RegisterForm, LoginForm, PostGameForm

# from forms import EditProfileForm, UserAddForm, LoginForm, MessageForm
from models import db, connect_db, User, Game

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///chessclub'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = RegisterForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
  """Handle user login."""

  form = LoginForm()

  if form.validate_on_submit():
      user = User.authenticate(form.username.data,
                                form.password.data)

      if user:
          do_login(user)
          flash(f"Hello, {user.username}!", "success")
          return redirect("/")

      flash("Invalid credentials.", 'danger')

  return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
  """Handle logout of user."""

  do_logout()
  flash('you have logged out successfully', 'success')
  return redirect('/login')

##############################################################################
## HOME ROUTE ###

@app.route('/')
def home():
    if g.user:
        games = Game.query.all()
        return render_template("home.html", user=g.user, games=games)
    return redirect('/signup')


##############################################################################
## Users ###

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


# @app.route('/users/<int:user_id>')
# def users_show(user_id):
#     """Show user profile."""

#     user = User.query.get_or_404(user_id)
#     likes = Likes.query.filter_by(user_id=user_id).all()

#     # snagging messages in order from the database;
#     # user.messages won't be in order by default
#     messages = (Message
#                 .query
#                 .filter(Message.user_id == user_id)
#                 .order_by(Message.timestamp.desc())
#                 .limit(100)
#                 .all())
#     return render_template('users/show.html', user=user, messages=messages)

####################################################################
### GAME ROUTES ####

##############################################################################
# Messages routes:

@app.route('/games/<user_id>/')
def show_user_games(user_id):
    """button to add a new game at top. 
       show a list of user games below"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    games = Game.query.filter(Game.user_id == user_id)

    return render_template('users/games.html', user=user, games=games)

@app.route('/games/game/<game_id>')
def show_game(game_id):
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
   
    game = Game.query.get_or_404(game_id)
    return render_template('users/game.html', game=game, user=g.user)


@app.route('/games/game/<game_id>/delete', methods=['POST'])
def delete_game(game_id):
    """delete a game if user posted game"""

    game = Game.query.get_or_404(game_id)
    if g.user_id == game.user_id:
        del game
        db.session.commit()
        
        flash('game deleted', 'danger')
        return redirect('/')
    else:
        flash('Access unauthorized.', 'danger')
        return redirect("/")


@app.route('/games/new', methods=['GET', 'POST'])
def add_game():
    """get or post add game  """
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = PostGameForm()

    if form.validate_on_submit():
        pgn = form.pgn.data
        game = Game(pgn=pgn, user_id=g.user.id)

        db.session.add(game)
        db.session.commit()

        return redirect(f'/games/{g.user.id}')

    return render_template('users/post_game.html', form=form, user=g.user)

