"""
Main server data model
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

from veripeditus.server.app import db

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(128))
    name = db.Column(db.String(64))
    email = db.Column(db.String(128))

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package = db.Column(db.String(128))
    name = db.Column(db.String(32))
    version = db.Column(db.String(16))
    description = db.Column(db.String(1024))
    author = db.Column(db.String(32))
    license = db.Column(db.String(32))

    __table_args__ = (db.UniqueConstraint('package', 'name', 'version', name='_name_version_uc'),)

class World(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    game = db.relationship("Game")
