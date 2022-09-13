
import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

import requests

from datetime import datetime

from forms import RegisterForm, LoginForm, PostGameForm, TagForm, SearchGamesForm

# from forms import EditProfileForm, UserAddForm, LoginForm, MessageForm
from models import db, connect_db, User, Game, Like, Tag, GameTag, GameTagLikes

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

@app.route('/', methods=['GET','POST'])
def home():

    if g.user:
            games = Game.query.all()
            tags = Tag.query.all()
       
            return render_template("home.html", user=g.user, games=games, likes=g.user.likes, tags=tags)

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

@app.route('/games/<user_id>/')
def show_user_games(user_id):
    """button to add a new game at top. 
       show a list of user games below"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    games = Game.query.filter(Game.user_id == user_id).all()

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
    """delete a game by user"""

    game = Game.query.get_or_404(game_id)
    if g.user.id == game.user_id:
        db.session.delete(game)
        db.session.commit()
        
        flash('game deleted', 'danger')
        return redirect('/')
    else:
        flash('Access unauthorized.', 'danger')
        return redirect("/")

@app.route('/games/game/<game_id>/edit', methods=['GET', 'POST'])
def edit_game(game_id):
    """ Edit a pgn that has been posted by user"""
    game = Game.query.get_or_404(game_id)
    form = PostGameForm(obj=game)

    if form.validate_on_submit():
        game.pgn = form.pgn.data
        game.title = form.title.data
        db.session.commit()
        
        flash('pgn updated', 'success')
        return redirect(f'/games/{g.user.id}')

    return render_template('users/post_game.html', form=form, user=g.user)


@app.route('/games/new', methods=['GET', 'POST'])
def add_game():
    """get or post add game  """
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = PostGameForm()
    tags = Tag.query.all()

    if form.validate_on_submit():
        pgn = form.pgn.data
        title = form.title.data
        game = Game(pgn=pgn, user_id=g.user.id, title=title)

        db.session.add(game)
        db.session.commit()

        flash('game added')
        return redirect(f'/games/{g.user.id}')

    return render_template('users/post_game.html', form=form, user=g.user, tags=tags)

@app.route('/games/find', methods=['GET', 'POST'])
def find_games():
    
    form = SearchGamesForm()
    if form.validate_on_submit():
        print('form validating')

        base_url = 'https://api.chess.com/pub/player/'
        footer_url = f'/games/{datetime.now().year}/{datetime.now().strftime("%m")}'
        username = form.search.data
        url = f'{base_url}{username}{footer_url}'

        resp = requests.get(url=url)
        data = resp.json()
        json_games= data['games']
    
        return render_template('users/search_games.html', json_games=json_games)

    return render_template('users/find_games.html', form=form, user=g.user)

@app.route('/games/import', methods=['GET', 'POST'])
def import_game():
    if request.form['pgn']:
        pgn_data = request.form['pgn']
    
    game = Game(pgn=pgn_data)
    form = PostGameForm(obj=game)

    if form.validate_on_submit():
     
        pgn = form.pgn.data
        title = form.title.data
    
        
        game = Game(pgn=pgn, user_id=g.user.id, title=title)
        db.session.add(game)
        db.session.commit()

        flash('imported game posted')
        return redirect('/')


    return render_template('users/post_game.html', form=form, user=g.user, tags=Tag.query.all())



####################################################################
### LIKE ROUTES ####

@app.route('/likes')
def show_user_likes():
    games = g.user.likes
    return render_template ('/users/likes.html', games=games, user=g.user, likes = g.user.likes)



@app.route('/users/delete_like/<game_id>', methods=['POST'])
def delete_like(game_id):
    if g.user:
        for like in Like.query.all():
            if int(like.game_id) == int(game_id) and int(like.user_id) == int(g.user.id):

                db.session.delete(like)
                db.session.commit()

                flash('like removed', 'danger')
                return redirect(request.referrer)
        
        flash('you havent liked this post')
        return redirect(request.referrer)

    flash('unauthorized', 'danger')
    return redirect('/')

@app.route('/users/add_like/<game_id>', methods=['POST'])
def add_like(game_id):
    if g.user:
        counter = 0
        for like in Like.query.all():
            if int(like.game_id) == int(game_id) and int(like.user_id) == int(g.user.id):
                counter += 1

        if counter < 1:
            new_like = Like(user_id = g.user.id, game_id = game_id )
            db.session.add(new_like)
            db.session.commit()
            flash('post liked', 'success')
            return redirect(request.referrer)
        else:
            flash('You already liked this post')
            return redirect(request.referrer)
    flash('acesss unauthorized')
    return redirect('/')

  

####################################################################
### Tag Routes ####

@app.route('/tags')
def show_tags():
    if g.user:
        tags = Tag.query.all()
        return render_template('tags/tags.html', tags=tags)

    flash('access unauthorized', 'danger')   
    return redirect ('/')

@app.route('/tags/new', methods=['GET', 'POST'])
def add_tag():

    if g.user:
        form = TagForm()
        if not form.validate_on_submit():
            return render_template('tags/add_tag.html', form=form)
        
        if form.validate_on_submit():
            name = form.name.data
            tag = Tag(name=name)

            db.session.add(tag)
            db.session.commit()



            return redirect('/tags')


@app.route("/games/game/<game_id>/tag", methods=['POST'])
def tag_game(game_id):

    if g.user:
        print('TAGGING')
        tag_id = int(request.form.get('tags'))
        user_id = g.user.id
        game_tag = GameTag.query.filter(GameTag.tag_id == tag_id and GameTag.game_id == game_id).first()

        if game_tag not in GameTag.query.filter(GameTag.game_id == game_id).all():
          
            game_tag = GameTag(game_id = game_id, tag_id=tag_id)
            db.session.add(game_tag)
            db.session.commit()
            game_tag_like = GameTagLikes(game_tag_id=game_tag.id, user_id = user_id)
            db.session.add(game_tag_like)
            db.session.commit()

            flash('tag created and upvoted')
            return redirect (request.referrer)

        game_tag_like = GameTagLikes.query.filter_by(game_tag_id=game_tag.id, user_id=user_id).first()
     
        if not game_tag_like:
            game_tag_like = GameTagLikes(game_tag_id = game_tag.id, user_id = user_id)
            db.session.add(game_tag_like)
            db.session.commit()

            flash('tag upvoted')
            return redirect (request.referrer)
        
        if int(game_tag_like.user_id) == int(g.user.id):
            db.session.delete(game_tag_like)
            db.session.commit()

            flash('tag upvote removed')
            return redirect(request.referrer)
        else:
            flash('nothing happened?')
            return redirect(request.referrer)
    if not g.user.id:
        flash('access unauthorized')
        return redirect(request.referrer)


@app.route('/games/search_by_tag')
def search_by_tag():
    tag_id = request.args['tag_id']
    games = []
    tags = Tag.query.all()
    for game in Game.query.all():
  
        for item in game.game_tags:
            if int(tag_id) == item.tags.id:
                games.append(game)
                break
    return render_template('home.html', user=g.user, games=games, likes=g.user.likes, tags=tags)

    
####################################################################
### Modal Popups ####

@app.route('/modal')
def show_modal():
    if g.user:
        games = Game.query.all()
        tags = Tag.query.all()
                
        return render_template("modal.html", user=g.user, games=games, likes=g.user.likes, tags=tags)
  