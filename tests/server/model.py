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

from veripeditus.server.model import Player
from veripeditus.server.app import db

import unittest

class ServerModelTests(unittest.TestCase):
    """ Tests that check data handling in server.model """

    def setUp(self):
        """ Sets up test data objects """

        self.test_player = Player()
        self.test_player.username = "test"
        self.test_player.password = "test"
        self.test_player.name = "test Player"
        self.test_player.email = "test@example.com"
        db.session.add(self.test_player)
        db.session.commit()

    def tearDown(self):
        """ Remove test object """

        db.session.delete(self.test_player)
        db.session.commit()

    def test_player_password_unrecoverable(self):
        """ Tests whether the password is hashed on setting it """

        # The password to use for testing
        import random, string
        test_pw_len = random.randint(8, 16)
        test_pw = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(test_pw_len))

        # Set the password on the test_player object
        self.test_player.password = test_pw

        # Check that the retrieved password is not the clear text string.
        # We need to retrieve it first to circumvent auto coercion.
        test_pw_hash = str(self.test_player.password.hash)
        self.assertNotEqual(test_pw_hash, test_pw)

    def test_player_password_verifies(self):
        """ Tests whether the hashed password verifies """

        # The password to use for testing
        import random, string
        test_pw_len = random.randint(8, 16)
        test_pw = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(test_pw_len))

        # Set the password on the test_player object
        self.test_player.password = test_pw

        # Check that, through auto coercion, the password can be verified
        # by direct comparison
        self.assertEqual(self.test_player.password, test_pw)
