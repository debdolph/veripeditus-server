from veripeditus.server.app import db
from veripeditus.server.app import app as application

application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/lib/veripeditus/veripeditus.db'
application.config['DEBUG'] = True
