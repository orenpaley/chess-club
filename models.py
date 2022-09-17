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
        db.ForeignKey('users.id', ondelete='cascade'),
    )

    game_id = db.Column(
        db.Integer,
        db.ForeignKey('games.id', ondelete='cascade')
    )
    
    __table_args__ = (db.UniqueConstraint(user_id, game_id),)


class GameTag(db.Model):
    """stores a game tag pair"""

    __tablename__ = 'game_tags'

    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey("tags.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)

    __table_args__ = (db.UniqueConstraint(game_id, tag_id),)

    game_tag_likes = db.relationship("GameTagLikes")
    tags = db.relationship("Tag")

class GameTagLikes(db.Model):
    """ automatically gets added to if already present in game tag table"""

    __tablename__ = 'game_tag_likes'
    id = db.Column(db.Integer, primary_key=True)
    game_tag_id = db.Column(db.Integer, db.ForeignKey("game_tags.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    __table_args__ = (db.UniqueConstraint(game_tag_id, user_id),)

    users = db.relationship("User")

### SPLIT GAME USER TAG TABLE 
## GAME_TAG_LIKES
    ### game_tag_id
    ### user_id (user who liked it)
## GAME_TAG_TABLE
    ### tag_id
    ### game_id
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
class Game(db.Model):
    """Each chess Game that has been uploaded or posted"""

    __tablename__ = 'games'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    title = db.Column(
        db.Text, 
        nullable=False)

    pgn = db.Column(
        db.Text, 
        nullable=False
    )

    timestamp = db.Column(
    db.DateTime,
    nullable=False,
    default=datetime.utcnow(),
    )

    likes = db.relationship('Like', backref='games')
   
    game_tags = db.relationship("GameTag")
class Tag(db.Model):

    __tablename__ = 'tags'
    
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
