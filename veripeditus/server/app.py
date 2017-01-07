"""
Flask application code for the Veripeditus server

This module contains everything to set up the Flask application.
"""

# veripeditus-server - Server component for the Veripeditus game framework
# Copyright (C) 2016  Dominik George <nik@naturalnet.de>
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
from flask_sqlalchemy import SQLAlchemy
from osmalchemy import OSMAlchemy

# Get a basic Flask application
APP = Flask(__name__)

# Default configuration
# FIXME allow modification after module import
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
APP.config['PASSWORD_SCHEMES'] = ['pbkdf2_sha512', 'md5_crypt']
APP.config['BASIC_REALM'] = "Veripeditus"

# Load configuration from a list of text files
CFGLIST = ['/var/lib/veripeditus/dbconfig.cfg', '/etc/veripeditus/server.cfg']
for cfg in CFGLIST:
    APP.config.from_pyfile(cfg, silent=True)

# Initialise SQLAlchemy and OSMAlchemy
DB = SQLAlchemy(APP)
OA = OSMAlchemy(DB, overpass=True)

# Import model and create tables
import veripeditus.server.model
DB.create_all()

# Run initialisation code
from veripeditus.server.control import init
init()

# Import REST API last
import veripeditus.server.rest
