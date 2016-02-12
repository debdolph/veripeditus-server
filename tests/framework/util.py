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

import os
import sys
import unittest

class GameDataTests(unittest.TestCase):
    """ Tests that check game data handling in framework.util """

    def setUp(self):
        """ Set up test cases """

        # Construct test data directory
        self.datadir = os.path.join(os.path.dirname(__file__), "data")

    def test_get_game_module(self):
        """ Test getting the game module (this is us) """

        from veripeditus.framework.util import get_game_module

        module = get_game_module()

        self.assertEqual(module, sys.modules[__name__])

    def test_get_game_module_name(self):
        """ Test getting the name of the game module (this is us) """

        from veripeditus.framework.util import get_game_module_name

        module = get_game_module_name()

        self.assertEqual(module, __name__)

    def test_get_game_data_file_name_image_png(self):
        """ Test getting the full path to an image resource in PNG format """

        resname = "testpng"
        restype = "image"

        from veripeditus.framework.util import get_game_data_file_name

        filename = get_game_data_file_name(restype, resname)

        # The returned path should match ower self-constructed datadir
        self.assertEqual(filename, os.path.join(self.datadir, restype, "%s.png" % resname))

    def test_get_game_data_file_image_png(self):
        """ Test getting a file object for an image resource in PNG format """

        resname = "testpng"
        restype = "image"

        from veripeditus.framework.util import get_game_data_file

        file = get_game_data_file(restype, resname)
        reffile = open(os.path.join(self.datadir, restype, "%s.png" % resname), "r")

        # The returned data should match the data in the test file
        self.assertEqual(file.read(), reffile.read())

        file.close()
        reffile.close()
