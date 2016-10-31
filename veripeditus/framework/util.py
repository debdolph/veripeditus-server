"""
Utility functions for framework components
"""

# veripeditus-server - Server component for the Veripeditus game framework
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

import os

import geopy

from veripeditus.server.app import DB
import veripeditus.framework

def get_image_path(game_mod, basename):
    """
    Get the path for an image file (.svg or .png, in order).

    Keyword arguments:

    game_mod -- reference to the game module
    basename -- name of the file without its extension
    """

    # Get module paths of framework and the provided game
    _path_framework = os.path.dirname(veripeditus.framework.__file__)
    _path_game = os.path.dirname(game_mod.__file__)

    # Get data sub-directories
    _respath_framework = os.path.join(_path_framework, "data")
    _respath_game = os.path.join(_path_game, "data")

    # Define extensions and paths to search
    _extensions = (".svg", ".png")
    _paths = (_respath_framework, _respath_game)

    # Define fallback image if nothing else is found
    _fallback = os.path.join(_respath_framework, "dummy.svg")

    # Generate a list of all possibilities
    _possibilities = ([os.path.join(_path, basename+_extension)
                       for _extension in _extensions
                       for _path in _paths] +
                      [_fallback])

    # Iterate over all possibilities and return the first existing resource
    for _possibility in _possibilities:
        if os.path.isfile(_possibility):
            return _possibility

def get_gameobject_distance(obj1, obj2):
    return gpxpy.geo.haversine_distance(obj1.latitude, obj1.longitude,
                                        obj2.latitude, obj2.longitude)

def add(obj):
    DB.session.add(obj)
    DB.session.commit()
