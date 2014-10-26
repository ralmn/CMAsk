import ast
from flask import Flask
from flask.ext.admin import Admin
from flask.ext.babel import Babel
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from flask.ext.script import Manager, Command, Server, Option
from flask.ext.migrate import Migrate, MigrateCommand
from flask_sockets import Sockets
from flask.ext.sqlalchemy import SQLAlchemy
import settings
import redis
import gevent


class VoteBackend(object):


    def __init__(self):
        self.clients = {}
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(settings.REDIS_CHAN)

    def __iter_data(self):
        for message in self.pubsub.listen():
            print(message)
            data = message.get('data')
            print(data)
            if message['type'] == 'message':
                print('ok ?')
                app.logger.info(u'Sending message: {}'.format(data))
                #data = ast.literal_eval(data)
                yield data

    def register(self, client, id):
        cls = []
        if id in self.clients:
            cls = self.clients[id]

        cls.append(client)
        self.clients[id] = cls
        print(self.clients)


    def send(self, client, data, id):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            client.send(str(data))
            print('send', client, data)
        except Exception:
            print('error :(')
            cls = self.clients.get(id)
            cls.remove(client)
            self.clients[id] = cls

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        for data in self.__iter_data():
            data = ast.literal_eval(data)
            id = data['id']
            if id and id in self.clients:
                for client in self.clients[id]:
                    gevent.spawn(self.send, client, data, id)
            else:
                if id:
                    print('no client ? ', self.clients)
                else:
                    print('no id')

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)

app = Flask(__name__, template_folder='cmask/template',  static_folder='cmask/static')


app.config.from_object(settings)


#Configuration
app.config['USER_ENABLE_USERNAME']        = True              # Register and Login with username
app.config['USER_ENABLE_EMAIL']           = True              # Register with email
app.config['USER_ENABLE_CONFIRM_EMAIL']   = True              # Require email confirmation
app.config['USER_ENABLE_CHANGE_USERNAME'] = False
app.config['USER_ENABLE_CHANGE_PASSWORD'] = False
app.config['USER_ENABLE_FORGOT_PASSWORD'] = False
app.config['USER_ENABLE_REGISTRATION'] = app.config['ALLOW_REGISTER']
app.config['USER_AFTER_LOGIN_ENDPOINT']   = 'views.index'
app.config['USER_LOGIN_TEMPLATE']         = "login.html"
app.config['USER_REGISTER_TEMPLATE']      = "register.html"
app.config['USER_CONFIRM_EMAIL_EMAIL_TEMPLATE']      = "email/register_confirm.html"
app.config['USER_APP_NAME']      = app.config['APP_NAME']

db = SQLAlchemy(app)

sockets = Sockets(app)

redis = redis.from_url(settings.BROKER_URL)

manager = Manager(app)

server = Server(host="0.0.0.0", port=5000, use_debugger=True, use_reloader=True)
serverProd = Server(host="0.0.0.0", port=5000, use_debugger=False, use_reloader=False)

manager.add_command('runserver', server)
manager.add_command('runserverprod', serverProd)

mail = Mail(app)                                # Initialize Flask-Mail
babel = Babel(app)                              # Initialize Flask-Babel

vote_backend = VoteBackend()
vote_backend.start()

loginManager = LoginManager(app=app)


class AdminCommand(Command):

    option_list = (
            Option('--addadmin', '-a', dest='addname'),
    )
    def run(self, addname = None):
        if addname is not None:
            from cmask.models import User
            user = User.query.filter_by(username=addname).first()
            if user is not None:
                user.admin = True
                db.session.commit()
                print("%s is now admin" % user.username)
            else:
                print('Not any user find for name %s' % addname)

manager.add_command("admin", AdminCommand)

def getAppName():
  return app.config.get('APP_NAME')

def getConfig():
    return app.config

@app.context_processor
def utility_processor():

    return dict(getAppName=getAppName, getConfig=getConfig)

import cmask.socket

if __name__ == '__main__' or __name__ == "uwsgi_file_app":



    from cmask import models
    models.user_manager.init_app(app)

    #Declare views
    from cmask.views import mod as modViews
    app.register_blueprint(modViews)

    #Declare models
    db.init_app(app)

    from cmask.admin import MyIndexView, MyAdminView

    miv = MyIndexView(template="admin_index.html")
    admin = Admin(app, index_view=miv)
    admin.add_view(MyAdminView(models.User, db.session))
    admin.add_view(MyAdminView(models.Vote, db.session))
    admin.add_view(MyAdminView(models.VoteOption, db.session))


    migrate = Migrate(app, db)
    #migrate.init_app(app, db)
    manager.add_command('db', MigrateCommand)


    #Init
if __name__ == "__main__":
    manager.run(default_command='runserverprod')
    #app.run(port=5000, debug=True)


