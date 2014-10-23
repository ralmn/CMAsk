from app import db, app, loginManager
from flask.ext.user import UserMixin, SQLAlchemyAdapter, UserManager

__author__ = 'ralmn'


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    personalized = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return '<Vote %s>' % self.name


class VoteOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Integer, default=0)
    vote_id = db.Column(db.Integer, db.ForeignKey('vote.id'))
    vote = db.relationship('Vote', backref='options')

    def slug(self):
        return self.name.replace(' ', '-')

    def __repr__(self):
        return '<VoteOption %s>' % self.name



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(50))
    email = db.Column(db.String(50))
    reset_password_token = db.Column(db.String(100), nullable=True, default="")
    confirmed_at = db.Column(db.DateTime(), nullable=True)
    active = db.Column(db.Boolean(), nullable=False, default=False)
    create = db.Column(db.Boolean(), nullable=False, default=False)

    def can_create(self):
        return self.create

db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter=db_adapter,login_manager=loginManager, app=app)     # Init Flask-User and bind to app
