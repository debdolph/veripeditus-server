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

from veripeditus.server.app import app, db

from sqlalchemy_utils import EmailType, PasswordType, UUIDType, force_auto_coercion
import uuid

# Activiate auto coercion of data types
force_auto_coercion()

class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(UUIDType(binary=False), unique=True, default=uuid.uuid4, nullable=False)

    created = db.Column(db.DateTime, default=db.func.now())
    updated = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class Player(Base):
    username = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(PasswordType(schemes=app.config['PASSWORD_SCHEMES']), nullable=False)
    name = db.Column(db.String(64))
    email = db.Column(EmailType)
    longitude = db.Column(db.Float, default=0.0, nullable=False)
    latitude = db.Column(db.Float, default=0.0, nullable=False)

playergroup = db.Table('playergroup',
                       db.Column('player_id', db.Integer, db.ForeignKey('player.id')),
                       db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
                      )

worldgroup = db.Table('worldgroup',
                      db.Column('world_id', db.Integer, db.ForeignKey('world.id')),
                      db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
                     )

class Group(Base):
    name = db.Column(db.String(64), unique=True, nullable=False)
    players = db.relationship('Player', secondary=playergroup,
                              backref=db.backref('groups', lazy='dynamic'))

class Game(Base):
    package = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    version = db.Column(db.String(16), nullable=False)
    description = db.Column(db.String(1024))
    author = db.Column(db.String(32))
    license = db.Column(db.String(32))

    __table_args__ = (db.UniqueConstraint('package', 'name', 'version', name='_name_version_uc'),)

class World(Base):
    name = db.Column(db.String(32), unique=True, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    game = db.relationship('Game', backref=db.backref('worlds', lazy='dynamic'))
    groups = db.relationship('Group', secondary=worldgroup,
                             backref=db.backref('groups', lazy='dynamic'))
