"""
Main server application
"""

# veripeditus-server - Server component for the Veripeditus game framework
# Copyright (C) 2016  Dominik George <nik@naturalnet.de>
# Copyright (c) 2015  Mirko Hoffmann <m.hoffmann@tarent.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager

app = Flask(__name__)
version = '0.1'

# FIXME allow modification after module import
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

cfglist = ['/etc/veripeditus/server.cfg']
for cfg in cfglist:
    app.config.from_pyfile(cfg, silent=True)

db = SQLAlchemy(app)
manager = APIManager(app, flask_sqlalchemy_db=db)

from veripeditus.server import model

db.create_all()

if __name__ == '__main__':
    app.debug = True
    app.run()
