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

from veripeditus.server.app import db
from veripeditus.server.model import Game
from veripeditus.server.util import get_games

def init():
    # Get all installed games
    games = get_games()

    # Iterate over package names and modules
    for package in games.keys():
        module = games[package]

        # Check if game is in database
        game = Game.query.filter_by(package=package, name=module.NAME,
                                            version=module.VERSION).first()

        # Create new object if nonexistent
        if game == None:
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
