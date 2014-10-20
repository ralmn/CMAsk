import sys
from flask import Flask
from flask.ext.script import Manager, Command

from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/hirel/questionLive.db'
db = SQLAlchemy(app)

manager = Manager(app)

class RunServer(Command):
    def run(self):
        app.run(port=5000, debug=True)

manager.add_command('runserver', RunServer)


if __name__ == '__main__' or __name__ == "uwsgi_file_cmask":

    #Declare views
    from cmask.views import mod as modViews
    app.register_blueprint(modViews)



    #Declare models
    db.init_app(app)

    from cmask import models


    migrate = Migrate(app, db)
    #migrate.init_app(app, db)
    manager.add_command('db', MigrateCommand)


    #Init
    app.debug=True
    manager.run(default_command='runserver')
    #app.run(port=5000, debug=True)