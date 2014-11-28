# coding=utf-8
import time
from app import db, app, loginManager
from flask.ext.user import UserMixin, SQLAlchemyAdapter, UserManager

__author__ = 'ralmn'


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    close = db.Column(db.DATETIME, nullable=True)
    open = db.Column(db.DATETIME, nullable=True)
    def __repr__(self):
        return '<Vote %s>' % self.name

    def closeTS(self):
        return int(time.mktime(self.close.timetuple()))
    def openTS(self):
        return int(time.mktime(self.open.timetuple()))

class VoteOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Integer, default=0)
    vote_id = db.Column(db.Integer, db.ForeignKey('vote.id'))
    vote = db.relationship('Vote', backref='options')

    def slug(self):
        ch1 = u"àâçéèêëîïôùûüÿ"
        ch2 = u"aaceeeeiiouuuy"
        s = ""
        for c in self.name:
            i = ch1.find(c)
            if i>=0:
                s += ch2[i]
            else:
                s += c
        slug = s.replace(' ', '-').replace("'",'-').replace('"','-')
        return slug

    def getName(self):
        import HTMLParser
        parser = HTMLParser.HTMLParser()
        s =  parser.unescape(self.name)
        return s.replace('"','\\"')

    def __repr__(self):
        return '<VoteOption %s %s>' % (self.vote.name, self.name)



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(50))
    email = db.Column(db.String(50))
    reset_password_token = db.Column(db.String(100), nullable=True, default="")
    confirmed_at = db.Column(db.DateTime(), nullable=True)
    active = db.Column(db.Boolean(), nullable=False, default=False)
    create = db.Column(db.Boolean(), nullable=False, default=False)
    admin = db.Column(db.Boolean(), nullable=True, default=False)

    def can_create(self):
        return self.create

db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter=db_adapter,login_manager=loginManager, app=app)     # Init Flask-User and bind to app

