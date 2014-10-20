from wtforms import Form, StringField, BooleanField
from cmask.models import Vote

class VoteForm(Form):
    name = StringField('Name')
    personalized = BooleanField("personalized")
