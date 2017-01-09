"""
Basic data model for core models of the Veripeditus server

These models are not used by games, they are only used by the
server core.
"""

# veripeditus-server - Server component for the Veripeditus game framework
# Copyright (C) 2016, 2017  Dominik George <nik@naturalnet.de>
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

# pragma pylint: disable=too-few-public-methods

from flask import g, redirect
from flask_restless import url_for
from sqlalchemy_utils import PasswordType, force_auto_coercion

from veripeditus.server.app import APP, DB
from veripeditus.server.auth import Roles
from veripeditus.server.util import api_method, get_game_by_name

# Activiate auto coercion of data types
force_auto_coercion()

class Base(DB.Model):
    """ Base class for all models in Veripeditus. """

    # Abstract model base, not created itself
    __abstract__ = True

    # Primary key numeric id for all objects
    # FIXME do we need the uuid?
    id = DB.Column(DB.Integer(), primary_key=True)

    # Timestamps for creation and any update, maintained automatically
    created = DB.Column(DB.DateTime(), default=DB.func.now())
    updated = DB.Column(DB.DateTime(), default=DB.func.now(),
                        onupdate=DB.func.now())

class User(Base):
    """ A user account in the Veripeditus webserver.

    This is not a player object, it is only used for authentication and to
    link players to it.
    """

    # Login credentials
    # Password is automatically maintained in encrypted form through the PasswordType
    username = DB.Column(DB.String(32), unique=True, nullable=False)
    password = DB.Column(PasswordType(schemes=APP.config['PASSWORD_SCHEMES']),
                         nullable=False)

    # Relationship to the currently active player object for this account
    current_player_id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject_player.id"))
    current_player = DB.relationship("veripeditus.framework.model.Player",
                                     foreign_keys=[current_player_id])

    # The role of this account in the server
#    role = DB.Column(DB.Enum(Roles), default=Roles.player, nullable=False)
    role = DB.Column(DB.Unicode(32), default="PLAYER", nullable=False)

    @staticmethod
    def get_authenticated(username, password):
        """ Return a User object if username and password match,
        or None otherwise.
        """

        # Filter for username first
        user = User.query.filter_by(username=username).first()

        # Compare password if a user was found
        if user and user.password == password:
            # Return found user
            return user
        else:
            # Fallback to None
            return None

class Game(Base):
    """ A game known to the server.

    This model/table is automatically filled with all games
    known to the server from the _sync_games() initialisation
    function.

    It is used to keep a mapping to game modules within the
    data model.
    """

    # Base name of the game's Python package
    package = DB.Column(DB.String(128), nullable=False)
    # Filled from the respective game constants
    name = DB.Column(DB.String(32), nullable=False)
    version = DB.Column(DB.String(16), nullable=False)
    description = DB.Column(DB.String(1024))
    author = DB.Column(DB.String(32))
    license = DB.Column(DB.String(32))

    # The triple package,name,version needs to be unique
    __table_args__ = (DB.UniqueConstraint('package', 'name', 'version',
                                          name='_name_version_uc'),)

    @property
    def module(self):
        """ Attribute pointing to the real Python module loaded for the game. """

        # Determine the game module from the package name
        return get_game_by_name(self.package)

    @api_method(authenticated=True)
    def world_create(self, name=None):
        """ Create a world with this game.

        Called as an API method from a client.
        """

        # Create a new World object and store in database
        world = World()
        if name is None:
            world.name = self.name
        else:
            world.name = name
        world.game = self
        DB.session.add(world)
        DB.session.commit()

        # Redirect to new World object
        return redirect("/api/world/%i" % world.id)

class World(Base):
    """ A gaming world with a specific game.

    This groups game objects together.
    """

    # Textual name of this world
    name = DB.Column(DB.String(32), unique=True, nullable=False)
    # Whether this world is enabled or not
    enabled = DB.Column(DB.Boolean(), default=True, nullable=False)

    # Relationship to the game played in this world
    game_id = DB.Column(DB.Integer, DB.ForeignKey('game.id'))
    game = DB.relationship('Game', backref=DB.backref('worlds',
                                                      lazy='dynamic'))

    @api_method(authenticated=True)
    def player_join(self):
        """ Make the current player join this world.

        Called as an API method from a client.
        """

        # Check whether a user is logged in
        if g.user is None:
            # FIXME proper error
            return None

        # Check whether the user has a player in this world
        player = Player.query.filter_by(user=g.user, world=self).scalar()
        if player is None:
            # Create a new player in this world
            player = self.game.module.Player()
            player.name = g.user.username
            player.world = self
            player.user = g.user
            DB.session.add(player)
            DB.session.commit()

        # Update current_player
        g.user.current_player = player
        DB.session.add(g.user)
        DB.session.commit()

        # Redirect to new player object
        return redirect(url_for(player.__class__, resource_id=player.id))
        return redirect("/api/gameobject_player/%i" % player.id)

# Import framework model here
# This needs to be at the bottom due to the (slightly complex) import
# structure of the project and because it uses the base models described
# in here
# pragma pylint: disable=unused-import
# pragma pylint: disable=wrong-import-position
import veripeditus.framework.model
from veripeditus.framework.model import Player
