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

import unittest

from veripeditus.server.app import APP

class ServerAppTests(unittest.TestCase):
    """ Tests that check game data handling in server.app """

    def test_app_init_sync_games(self):
        """ Test whether the test game is known in the database """

        # Get first known game from ORM
        from veripeditus.server.model import Game
        first_game = Game.query.filter_by(package="test").first()

        # Get module of test game
        import veripeditus.game.test as first_game_module

        # Verify all fields
        self.assertEqual(first_game.package, "test")
        self.assertEqual(first_game.name, first_game_module.NAME)
        self.assertEqual(first_game.description, first_game_module.DESCRIPTION)
        self.assertEqual(first_game.author, first_game_module.AUTHOR)
        self.assertEqual(first_game.license, first_game_module.LICENSE)
        self.assertEqual(first_game.version, first_game_module.VERSION)

    def test_app_init_add_data_user(self):
        """ Test whether a test user is known in the database """

        # Get first known admin user from ORM
        from veripeditus.server.model import User
        user = User.query.filter_by(username="admin").first()

        self.assertEqual(user.username, "admin")
        self.assertEqual(user.password, "admin")
        self.assertEqual(user.name, "The Boss")
        self.assertEqual(user.email, "theboss@example.com")
        self.assertLessEqual(user.active_player.longitude, 180.0)
        self.assertGreaterEqual(user.active_player.longitude, -180.0)
        self.assertLessEqual(user.active_player.latitude, 90.0)
        self.assertGreaterEqual(user.active_player.latitude, -90.0)
