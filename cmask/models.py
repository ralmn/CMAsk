from app import db

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


