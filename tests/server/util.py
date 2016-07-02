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

class ServerUtilTests(unittest.TestCase):
    """ Tests that check game data handling in server.util """

    def test_get_game_names(self):
        """ Test getting a list of names of available game packages """

        from veripeditus.server.util import get_game_names

        # Get game names
        games = get_game_names()

        # Returned object should be a list
        self.assertIsInstance(games, list)

        # Returned object should contain the test game
        self.assertIn("test", games)

    def test_get_games(self):
        """ Test getting a list game modules """

        from veripeditus.server.util import get_games

        # Get game module objects
        games = get_games()

        # Returned object should be a dict
        self.assertIsInstance(games, dict)

        # test should be a key
        self.assertIn("test", games)

        # The test key should refer to the test game module
        import veripeditus.game.test as testgame
        self.assertIs(games["test"], testgame)
