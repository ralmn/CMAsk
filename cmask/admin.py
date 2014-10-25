from app import db, babel
from flask.ext.admin import AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from sqlalchemy.exc import OperationalError

__author__ = 'ralmn'

class MyIndexView(AdminIndexView):
    def is_accessible(self):
        from flask.ext.login import current_user
        try:
            username = current_user.username
        except OperationalError:
            print("error reload")
            db.session.rollback()
            db.engine.connect()
        if current_user.is_authenticated():
            return current_user.admin and current_user.admin == True
        return False

    def __init__(self, name=None, category=None,
                 endpoint=None, url=None,
                 template='admin/index.html'):
        super(MyIndexView, self).__init__(name or 'Home',
                                             category,
                                             endpoint or 'admin',
                                             url or '/admin',
                                             'static')
        self._template = template


class MyAdminView(ModelView):

    def is_accessible(self):
        from flask.ext.login import current_user
        try:
            username = current_user.username
        except OperationalError:
            print("error reload")
            db.session.rollback()
            db.engine.connect()
        db.session.flush()
        if current_user.is_authenticated():
           return current_user.admin and current_user.admin == True
        return False