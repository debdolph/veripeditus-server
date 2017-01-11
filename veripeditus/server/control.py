"""
Control routines for the Veripeditus server

This module contains routines bound to the webapp but not
used directly in views.
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
from flask import request, Response, g

from veripeditus.framework.model import GameObject
from veripeditus.server.app import DB, APP
from veripeditus.server.auth import Roles
from veripeditus.server.model import User, Game, World
from veripeditus.server.util import get_games

def _sync_games():
    """ Find all installed games and sync them to the database. """

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
    """ Create example data (only if database was unused, e.g. no User
    exists).
    """

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
    # FIXME make this configurable
    # FIXME move to own function or drop
    if os.path.isfile("/etc/veripeditus/accounts.lst"):
        # Open accounts list file and load entries from it
        with open("/etc/veripeditus/accounts.lst", "r") as file:
            for line in file.readlines():
                # Split username and password from line
                username, password = line.strip().split(" ")

                # Create user if a user with this name does not exist
                if not User.query.filter_by(username=username).scalar():
                    user = User()
                    user.username = username
                    user.password = password
                    user.name = username
                    DB.session.add(user)

        # Commit to database at the end
        DB.session.commit()

def init():
    """ Initialise server by calling some setup routines. """

    _sync_games()
    _add_data()

@APP.before_request
def _check_auth():
    """ Check any HTTP Authorization header before a request.

    This function sets the g.user object to the logged-in user.
    if any, or to None.
    """

    # Default to None
    g.user = None

    # Look for Authorization header
    if request.authorization:
        # Load user and store it in Flask globals
        g.user = User.get_authenticated(request.authorization.username,
                                        request.authorization.password)

def needs_authentication():
    """ Helper function that returns a WWW_Authenticate response
    if something requires authentication.
    """

    # Construct 401 response with WWW-Authenticate header
    return Response('Authentication failed.', 401,
                    {'WWW-Authenticate': 'Basic realm="%s"'
                                         % APP.config['BASIC_REALM']})

@APP.after_request
def _run_spawns(res):
    """ Function run after every request to handle spawns of game objects. """
    # FIXME come up with something more efficient

    # Iterate over all known game object classes
    for gameobject in GameObject.__subclasses__():
        # Run spawn code
        gameobject.spawn()

    # Return original response unchanged
    return res
