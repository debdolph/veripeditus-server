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

from veripeditus.server.app import APP, DB
from veripeditus.server.util import get_game_by_name

from flask import g
from sqlalchemy_utils import (EmailType, PasswordType, UUIDType,
                              force_auto_coercion)
import base64
import os
from uuid import uuid4

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

class UsersToRoles(Base):
    __tablename__ = "users_to_roles"

    user_id = DB.Column(DB.Integer(), DB.ForeignKey('user.id'))
    role_id = DB.Column(DB.Integer(), DB.ForeignKey('role.id'))

class User(Base):
    username = DB.Column(DB.String(32), unique=True, nullable=False)
    password = DB.Column(PasswordType(schemes=APP.config['PASSWORD_SCHEMES']),
                         nullable=False)
    name = DB.Column(DB.String(64))
    email = DB.Column(EmailType())

    current_player_id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject_player.id"))
    current_player = DB.relationship("Player",
                                     foreign_keys=[current_player_id])

    roles = DB.relationship("Role", secondary=UsersToRoles, backref="users")

    @staticmethod
    def get_authenticated(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            return user
        else:
            return None

class Role(Base):
    name = DB.Column(DB.String(32), unique=True, nullable=False)

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

class World(Base):
    name = DB.Column(DB.String(32), unique=True, nullable=False)
    game_id = DB.Column(DB.Integer, DB.ForeignKey('game.id'))
    game = DB.relationship('Game', backref=DB.backref('worlds',
                                                      lazy='dynamic'))
    enabled = DB.Column(DB.Boolean())

from veripeditus.framework.model import *
