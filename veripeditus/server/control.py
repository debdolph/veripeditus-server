"""
Main server control code
"""

# veripeditus-server - Server component for the Veripeditus game framework
# Copyright (C) 2016  Dominik George <nik@naturalnet.de>
# Copyright (C) 2016  Eike Tim Jesinghaus <eike@naturalnet.de>
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

import os
import random
from flask import request, Response, g


from veripeditus.server.app import DB, APP
from veripeditus.server.auth import Roles
from veripeditus.server.model import *
from veripeditus.server.util import get_games

def _sync_games():
    # Get all installed games
    games = get_games()

    # Iterate over package names and modules
    for package in games.keys():
        module = games[package]

        # Check if game is in database
        game = Game.query.filter_by(package=package, name=module.NAME,
                                    version=module.VERSION).first()

        # Create new object if nonexistent
        if game is None:
            game = Game()

        # Sync metadata to database class
        game.package = package
        game.name = module.NAME
        game.version = module.VERSION
        game.description = module.DESCRIPTION
        game.author = module.AUTHOR
        game.license = module.LICENSE

        # Write to database
        DB.session.add(game)
        DB.session.commit()

def _add_data():
    # Create example data (only if database was unused, e.g. no User
    # exists)

    # Return if a User exists
    if len(User.query.all()) == 0:
        # Create new user and world
        user = User()
        user.username = "admin"
        user.password = "admin"
        user.name = "The Boss"
        user.email = "theboss@example.com"
#        user.role = Roles.admin
        user.role = "ADMIN"
        world = World()
        world.name = "Default World"
        world.game = Game.query.first()
        DB.session.add(user)
        DB.session.add(world)
        DB.session.commit()

    # Check for existance of account list file
    if os.path.isfile("/etc/veripeditus/accounts.lst"):
        with open("/etc/veripeditus/accounts.lst", "r") as file:
            for line in file.readlines():
                username, password = line.strip().split(" ")
                if not User.query.filter_by(username=username).scalar():
                    user = User()
                    user.username = username
                    user.password = password
                    user.name = username
                    DB.session.add(user)
        DB.session.commit()

def init():
    _sync_games()
    _add_data()

@APP.before_request
def _check_auth():
    g.user = None

    if request.authorization:
        g.user = User.get_authenticated(request.authorization.username,
                                        request.authorization.password)

def needs_authentication():
    return Response('Authentication failed.', 401,
                    {'WWW-Authenticate': 'Basic realm="%s"'
                                         % APP.config['BASIC_REALM']})

@APP.after_request
def _run_spawns(res):
    for go in GameObject.__subclasses__():
        go.spawn()
    return res
