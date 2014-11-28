from wtforms import Form, StringField, BooleanField
from cmask.models import Vote

class VoteForm(Form):
    name = StringField('Nom du vote')
    personalized = BooleanField("Mode Vrai/Faux", default=True)
    closed = BooleanField('Ouverture et fermeture automatique')
    openDate = StringField('')
    openTime = StringField('')
    closeDate = StringField('')
    closeTime = StringField('')
