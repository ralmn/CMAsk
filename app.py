import ast
from flask import Flask
from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from flask.ext.script import Manager, Command, Server
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
            print('data',data)
            data = ast.literal_eval(data)
            print('data',data, data['id'])
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

app = Flask(__name__)
app.config.from_object(settings)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/ralmn/questionLive.db'
db = SQLAlchemy(app)

sockets = Sockets(app)

redis = redis.from_url(settings.BROKER_URL)

manager = Manager(app)

server = Server(host="0.0.0.0", port=5000, use_debugger=True, use_reloader=True)

manager.add_command('runserver', server)

mail = Mail(app)                                # Initialize Flask-Mail

vote_backend = VoteBackend()
vote_backend.start()

loginManager = LoginManager(app=app)


import cmask.socket

if __name__ == '__main__' or __name__ == "uwsgi_file_cmask":

    from cmask import models
    models.user_manager.init_app(app)

    #Declare views
    from cmask.views import mod as modViews
    app.register_blueprint(modViews)

    #Declare models
    db.init_app(app)


    migrate = Migrate(app, db)
    #migrate.init_app(app, db)
    manager.add_command('db', MigrateCommand)


    #Init
    app.debug=True
    manager.run(default_command='runserver')
    #app.run(port=5000, debug=True)


