"""
Utility functions for framework components
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

import os
import sys

class NoSuchResourceError(Exception):
    """ Thrown when a resource cannot be found in a game data directory. """

    pass

def get_game_data_file(module, restype, basename):
    """
    Get the full path of a game data resource.

    Keyword arguments:

    module -- name of the game module (veripeditus.game.foo)
    restype -- type of the resource to be loaded; one of:
               image - for image files
    basename -- basename of the file to find; without extension
                so a logical decision can be made by type
    """

    # Get the path of the module implementation
    _modpath = os.path.dirname(sys.modules[module].__file__)
    # Get path of data directory for given type
    _respath = os.path.join(_modpath, "data", restype)

    # Logic depending on resource type to be loaded
    if restype == "image":
        # Check whether a PNG file exists
        _file = os.path.join(_respath, "%s.png" % basename)
        if os.path.isfile(_file):
            return _file

    # If we got here, no logic matched
    raise NoSuchResourceError("No resource found for game %s, type %s, called %s."
                              % (module, restype, basename))
