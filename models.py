"""SQLAlchemy models for Chess Club."""

from datetime import datetime
from sqlite3 import IntegrityError

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()





class Like(db.Model):
    """Mapping user likes to warbles."""

    __tablename__ = 'likes' 

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    game_id = db.Column(
        db.Integer,
        db.ForeignKey('games.id', ondelete='cascade'),
        unique=True
    )




class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    email = db.Column(
    db.Text,
    nullable=False,
    unique=True,
)
    first_name = db.Column(
        db.Text, 
        nullable=True
    )

    last_name = db.Column(
    db.Text, 
    nullable=True
)

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )

    location = db.Column(
    db.Text,
    nullable=True
)

    bio = db.Column(
        db.Text,
        nullable=True
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    ### TODO ########
    ## ADD FRIENDS TO MODEL ##

    likes = db.relationship(
        'Game',
        secondary="likes",
        backref='games'
    )

    games = db.relationship(
        'Game', backref='users'
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """
        
        if cls.query.filter_by(username=username).first():
            raise IntegrityError

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url
        )
        
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('games.id'), primary_key=True)
)

class Game(db.Model):
    """Each chess Game that has been uploaded or posted"""

    __tablename__ = "games"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    pgn = db.Column(
        db.Text, 
        nullable=False
    )

    event = db.Column(
        db.String(50)
    )

    timestamp = db.Column(
    db.DateTime,
    nullable=False,
    default=datetime.utcnow(),
    )

    white = db.Column(
        db.String(50), 
        nullable=False, 
        default='???'
    )

    black = db.Column(
    db.String(50), 
    nullable=False, 
    default='???'
    )

    result = db.Integer()

    likes = db.relationship('Like', backref='games')
    
    tags = db.relationship(
    'Tag', secondary=tags, backref='games'
)
class Tag(db.Model):
    
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(50),
        nullable=False, 
        unique=True
    )

def connect_db(app):
    """initialize app """

    db.app = app
    db.init_app(app)
