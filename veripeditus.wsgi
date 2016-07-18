from veripeditus.server.app import DB
from veripeditus.server.app import APP as application

application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/lib/veripeditus/veripeditus.db'
application.config['DEBUG'] = True
