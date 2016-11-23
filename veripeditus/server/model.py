"""
Main server data model
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

from uuid import uuid4

from flask import g, redirect
from sqlalchemy_utils import (EmailType, PasswordType, UUIDType,
                              force_auto_coercion)

from veripeditus.server.app import APP, DB
from veripeditus.server.auth import Roles
from veripeditus.server.util import api_method, get_game_by_name

# Activiate auto coercion of data types
force_auto_coercion()

class Base(DB.Model):
    __abstract__ = True

    id = DB.Column(DB.Integer(), primary_key=True)
    uuid = DB.Column(UUIDType(binary=False), unique=True, default=uuid4,
                     nullable=False)

    created = DB.Column(DB.DateTime(), default=DB.func.now())
    updated = DB.Column(DB.DateTime(), default=DB.func.now(),
                        onupdate=DB.func.now())

    api_exclude = []

class User(Base):
    username = DB.Column(DB.String(32), unique=True, nullable=False)
    password = DB.Column(PasswordType(schemes=APP.config['PASSWORD_SCHEMES']),
                         nullable=False)
    name = DB.Column(DB.String(64))
    email = DB.Column(EmailType())

    current_player_id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject_player.id"))
    current_player = DB.relationship("veripeditus.framework.model.Player",
                                     foreign_keys=[current_player_id])

#    role = DB.Column(DB.Enum(Roles), default=Roles.player, nullable=False)
    role = DB.Column(DB.Unicode(32), default="PLAYER", nullable=False)

    @staticmethod
    def get_authenticated(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            return user
        else:
            return None

class Game(Base):
    package = DB.Column(DB.String(128), nullable=False)
    name = DB.Column(DB.String(32), nullable=False)
    version = DB.Column(DB.String(16), nullable=False)
    description = DB.Column(DB.String(1024))
    author = DB.Column(DB.String(32))
    license = DB.Column(DB.String(32))

    __table_args__ = (DB.UniqueConstraint('package', 'name', 'version',
                                          name='_name_version_uc'),)

    @property
    def module(self):
        return get_game_by_name(self.package)

    @api_method(authenticated=True)
    def world_create(self):
        world = World()
        world.name = self.name
        world.game = self
        DB.session.add(world)
        DB.session.commit()

        # Redirect to new player object
        return redirect("/api/world/%i" % world.id)

class World(Base):
    name = DB.Column(DB.String(32), unique=True, nullable=False)
    game_id = DB.Column(DB.Integer, DB.ForeignKey('game.id'))
    game = DB.relationship('Game', backref=DB.backref('worlds',
                                                      lazy='dynamic'))
    enabled = DB.Column(DB.Boolean(), default=True, nullable=False)

    @api_method(authenticated=True)
    def player_join(self):
        # Check whether a user logged in
        if g.user is None:
            # FIXME proper error
            return None

        # Check whether the user has a player in this world
        player = Player.query.filter_by(user=g.user, world=self).scalar()
        if player is None:
            # Create a new player in this world
            player = self.game.module.Player()
            player.name = g.user.name
            player.world = self
            player.user = g.user
            DB.session.add(player)
            DB.session.commit()

        # Update current_player
        g.user.current_player = player
        DB.session.add(g.user)
        DB.session.commit()

        # Redirect to new player object
        return redirect("/api/gameobject_player/%i" % player.id)

from veripeditus.framework.model import *
