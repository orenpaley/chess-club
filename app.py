
import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

import requests

from forms import RegisterForm, LoginForm, PostGameForm, TagForm, SearchGamesForm, UserProfileForm

# from forms import EditProfileForm, UserAddForm, LoginForm, MessageForm
from models import db, connect_db, User, Game, Like, Tag, GameTag, GameTagLikes

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql://oren:psqloren@localhost/chessbyte'))

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
    """ Renders homepage view game posts"""

    if g.user:
            games = Game.query.all()
            tags = Tag.query.all()
       
            return render_template("home.html", user=g.user, games=games, likes=g.user.likes, tags=tags)

    return redirect('/signup')

@app.route('/newest')
def home_sort_newest():
    """sorts homepage by newest post"""
    if g.user:
        games = Game.query.order_by(Game.timestamp.desc()).all()
        tags = Tag.query.all()
    
        return render_template("home.html", user=g.user, games=games, likes=g.user.likes, tags=tags)

    return redirect('/signup')

@app.route('/oldest')
def home_sort_oldest():
    """sorts homepage by oldest post"""

    if g.user:
        games = Game.query.order_by(Game.timestamp).all()
        tags = Tag.query.all()

        return render_template("home.html", user=g.user, games=games, likes=g.user.likes, tags=tags)

    return redirect('/signup')
 

@app.route('/by_user_A_Z')
def home_sort_user_a_z():
    """sorts homepage by user a first"""

    if g.user:
        games = Game.query.all()
        tags = Tag.query.all()

        def sort_by_username(e):
            return e.users.username

        games.sort(key=sort_by_username)

        return render_template("home.html", user=g.user, games=games, likes=g.user.likes, tags=tags)

    return redirect('/signup')

@app.route('/by_user_Z_A')
def home_sort_user_z_a():
    """sorts homepage by user a last"""

    if g.user:
        games = Game.query.all()
        tags = Tag.query.all()

        def sort_by_username(e):
            return e.users.username

        games.sort(key=sort_by_username, reverse=True)


        return render_template("home.html", user=g.user, games=games, likes=g.user.likes, tags=tags)

    return redirect('/signup')

@app.route('/by_title_A_Z')
def home_sort_title_a_z():
    """sorts homepage by post title a first"""

    if g.user:
        games = Game.query.all()
        tags = Tag.query.all()

        def sort_by_title(e):
            return e.title.lower()
        
        games.sort(key=sort_by_title)

        return render_template("home.html", user=g.user, games=games, likes=g.user.likes, tags=tags)

    return redirect('/signup')

@app.route('/by_title_Z_A')
def home_sort_title_z_a():
    """sorts homepage by title a last"""
    
    if g.user:
        games = Game.query.all()
        tags = Tag.query.all()

        def sort_by_title(e):
            return e.title.lower()
        
        games.sort(key=sort_by_title, reverse=True)

        return render_template("home.html", user=g.user, games=games, likes=g.user.likes, tags=tags)

    return redirect('/signup')

@app.route('/by_most_likes')
def home_sort_most_likes():
    """sorts homepage by most likes"""
    
    if g.user:
        games = Game.query.all()
        tags = Tag.query.all()

        def sort_by_most_likes(e):
            return len(e.likes)
        
        games.sort(key=sort_by_most_likes, reverse=True)

        return render_template("home.html", user=g.user, games=games, likes=g.user.likes, tags=tags)

    return redirect('/signup')

@app.route('/by_least_likes')
def home_sort_least_likes():
    """sorts homepage by most likes"""
    
    if g.user:
        games = Game.query.all()
        tags = Tag.query.all()

        def sort_by_least_likes(e):
            return len(e.likes)
        
        games.sort(key=sort_by_least_likes)

        return render_template("home.html", user=g.user, games=games, likes=g.user.likes, tags=tags)

    return redirect('/signup')

@app.route('/by_most_tags')
def home_sort_most_tags():
    """sorts homepage by most unique tags"""
    
    if g.user:
        games = Game.query.all()
        tags = Tag.query.all()

        def sort_by_most_tags(e):
            return len(e.game_tags)
        
        games.sort(key=sort_by_most_tags, reverse=True)

        return render_template("home.html", user=g.user, games=games, likes=g.user.likes, tags=tags)

    return redirect('/signup')

@app.route('/by_least_tags')
def home_sort_least_tags():
    """sorts homepage by most unique tags"""
    
    if g.user:
        games = Game.query.all()
        tags = Tag.query.all()

        def sort_by_least_tags(e):
            return len(e.game_tags)
        
        games.sort(key=sort_by_least_tags)

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

@app.route('/users/me', methods=['GET', 'POST'])
def edit_user_profile():
    form = UserProfileForm(obj=g.user)
    user = g.user

    if g.user:
        if form.validate_on_submit():
            user.first_name = form.first_name.data 
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.location = form.location.data
            user.bio = form.bio.data

            db.session.commit()

            flash('profile updated', 'success')
            return redirect(request.referrer)
        
        return render_template('users/my_profile.html', user=g.user, form=form)


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
    if int(g.user.id) == int(game.user_id):
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
        return render_template('users/tag_new_game.html', tags=tags, game=game, user = g.user)

    return render_template('users/post_game.html', form=form, user=g.user, tags=tags)

@app.route('/games/find', methods=['GET', 'POST'])
def find_games():
    
    form = SearchGamesForm()
    if form.validate_on_submit():
        print('form validating')

        base_url = 'https://api.chess.com/pub/player'
        username = form.username.data
        year = form.year.data
        month = form.month.data
        offset = form.offset.data
        limit = form.limit.data


        url = f'{base_url}/{username}/games/{year}/{month:02d}'

        resp = requests.get(url=url)
        data = resp.json()
        json_games= data['games']
    
        return render_template('users/search_games.html', json_games=json_games, offset=offset, limit=offset+limit)

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

        tags= Tag.query.all()
        game = Game.query.get_or_404(game.id)

        flash('imported game posted')
        return render_template('users/tag_new_game.html', tags=tags, game=game, user = g.user)


    return render_template('users/post_game.html', form=form, user=g.user, tags=Tag.query.all())

@app.route('/games/new/<game_id>/add_tags', methods=['POST'])
def add_tags_to_new_game(game_id):

    for tag in Tag.query.all():
    
        if bool(request.form.get(tag.name)) == True:
         
            tag_id = int(request.form.get(tag.name))
            game_tag = GameTag(game_id=game_id, tag_id=tag_id)
            db.session.add(game_tag)
            db.session.commit()
            game_tag_like = GameTagLikes(game_tag_id=game_tag.id, user_id=g.user.id)
            db.session.add(game_tag_like)
            db.session.commit()
            print('game tagged HERE')
            continue;
       
            
       
    flash('game added and tagged')
    return redirect('/')

@app.route('/games/new/<game_id>/posted/tag')
def add_tags_to_new_post(game_id):

    game = Game.query.get_or_404(game_id)
    tags = Tag.query.all()

    if request.post:
        # tags = request.form.get('tags')
        return redirect('/')

    return render_template('tag_new_game.html', game=game, tags=tags)




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
            
            try:
                game_tag = GameTag(game_id = game_id, tag_id=tag_id)
                db.session.add(game_tag)
                db.session.commit()

            except IntegrityError:
             
                db.session.rollback()
                game_tag = GameTag.query.filter_by(game_id = game_id, tag_id=tag_id).first()
                gtl = GameTagLikes.query.filter_by(game_tag_id = game_tag.id, user_id = g.user.id).first()
                if gtl in GameTagLikes.query.all():
                    gtl.delete()
                    db.session.commit()

        
                    flash('tag like removed')
                    return redirect(request.referrer)

                else:  
                    gtl = GameTagLikes(game_tag_id=game_tag.id, user_id=g.user.id)
                    db.session.add(gtl)
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

@app.route("/games/game/<game_id>/tag/<tag_id>", methods=['POST'])
def tag_game_with_tag_button(game_id, tag_id):

    if g.user:
        print('TAGGING')
        tag_id = int(tag_id)
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

