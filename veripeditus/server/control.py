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

import random

from veripeditus.server.app import db
from veripeditus.server.model import Game, Player
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
        db.session.add(game)
        db.session.commit()

def _add_data():
    # Create example data (only if database was unused, e.g. no Player
    # exists)

    # Return if a Player exists
    if len(Player.query.all()) == 0:
        # Create new player
        player = Player()
        player.username = "admin"
        player.password = "admin"
        player.name = "The Boss"
        player.email = "theboss@example.com"
        player.longitude = random.uniform(-180.0, 180.0)
        player.latitude = random.uniform(-90.0, 90.0)
        # Add player to database
        db.session.add(player)
        db.session.commit()

def init():
    _sync_games()
    _add_data()
