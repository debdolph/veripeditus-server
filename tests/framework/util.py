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
from wand.image import Image

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
        reffile = open(os.path.join(self.datadir, restype, "%s.png" % resname), "rb")

        # The returned data should match the data in the test file
        self.assertEqual(file.read(), reffile.read())

        file.close()
        reffile.close()

    def test_get_game_data_file_name_enoent(self):
        """ Test getting the full path to a non-existent resource """

        resname = "enoent"
        restype = "image"

        from veripeditus.framework.util import get_game_data_file_name, NoSuchResourceError

        with self.assertRaises(NoSuchResourceError):
            get_game_data_file_name(restype, resname)

    def test_get_game_data_file_name_text(self):
        """ Test getting the full path to a text resource """

        resname = "testtxt"
        restype = "text"

        from veripeditus.framework.util import get_game_data_file_name

        filename = get_game_data_file_name(restype, resname)

        # The returned path should match ower self-constructed datadir
        self.assertEqual(filename, os.path.join(self.datadir, restype, "%s.txt" % resname))

    def test_get_game_data_file_text(self):
        """ Test getting a file object for a text resource """

        resname = "testtxt"
        restype = "text"

        from veripeditus.framework.util import get_game_data_file

        file = get_game_data_file(restype, resname)
        reffile = open(os.path.join(self.datadir, restype, "%s.txt" % resname), "r", encoding="utf-8")

        # The returned data should match the data in the test file
        self.assertEqual(file.read(), reffile.read())

        file.close()
        reffile.close()

    def test_get_game_data_file_text_mode(self):
        """ Test getting the right file mode for a text resource """

        resname = "testtxt"
        restype = "text"

        from veripeditus.framework.util import get_game_data_file

        file = get_game_data_file(restype, resname)

        # The returned file object should be in read mode and not binary
        self.assertEqual(file.mode, "r")

        file.close()

    def test_get_game_data_file_image_mode(self):
        """ Test getting the right file mode for an image resource """

        resname = "testpng"
        restype = "image"

        from veripeditus.framework.util import get_game_data_file

        file = get_game_data_file(restype, resname)

        # The returned file object should be in read mode and binary
        self.assertEqual(file.mode, "rb")

        file.close()

    def test_get_game_data_file_mode_manual(self):
        """ Test getting the right file mode via argument """

        resname = "testpng"
        restype = "image"

        from veripeditus.framework.util import get_game_data_file

        file = get_game_data_file(restype, resname, "r")

        # The returned file object should be in read mode and not binary
        self.assertEqual(file.mode, "r")

        file.close()

    def test_get_game_data_object_image_png(self):
        """ Test getting an Image object form a PNG resource """

        resname = "testpng"
        restype = "image"

        from veripeditus.framework.util import get_game_data_object

        obj = get_game_data_object(restype, resname)

        # Returned object should be an Image instance
        self.assertTrue(isinstance(obj, Image))

        # Verify size
        self.assertEqual(obj.size, (192, 192))

    def test_get_game_data_object_text(self):
        """ Test getting a list of strings from a TXT resource """

        resname = "testtxt"
        restype = "text"

        from veripeditus.framework.util import get_game_data_object

        obj = get_game_data_object(restype, resname)

        # Returned object should be a list
        self.assertTrue(isinstance(obj, list))

        # Verify size
        self.assertEqual(len(obj), 3)
