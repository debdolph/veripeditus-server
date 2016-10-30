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

import importlib
import os
import pkgutil
import sys

def get_game_names():
    """
    Get a list of names of installed games.

    Returns only the base name, i.e. the third part of the package name
    veripeditus.game.foo.
    """

    # Get all modules inside the namespace package veripeditus.game
    import veripeditus.game
    _pkgs = [i[1] for i in pkgutil.iter_modules(veripeditus.game.__path__)]

    return _pkgs

def get_games():
    """
    Get a list of installed game modules

    Returns a dictionary like {name: module}
    """

    # Get game names and import modules, build dict
    _pkgs = {i: importlib.import_module("veripeditus.game." + i)
             for i in get_game_names()}

    return _pkgs

def get_game_by_name(name):
    """
    Get a game module object by its name.
    """

    return get_games()[name]

def get_data_path():
    """
    Get the full path of the server module data directory.
    """

    # Get the path of the module implementation
    _modpath = os.path.dirname(sys.modules["veripeditus.server"].__file__)
    # Get path of data directory
    _respath = os.path.join(_modpath, "data")

    return _respath

def api_method(f):
    """ Decorator to mark a method as runnable by the REST API. """
    f.is_api_method = True
    return f
