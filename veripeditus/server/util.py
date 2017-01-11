"""
Utility functions for Veripeditus server code.

This module contains functions that are used to achieve various
things within the rest of the code, but are not called directly
for views or control.
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

import magic

def get_game_names():
    """
    Get a list of names of installed games.

    Returns only the base name, i.e. the third part of the package name
    veripeditus.game.foo.
    """

    # Get all modules inside the namespace package veripeditus.game
    # pragma pylint: disable=no-name-in-module
    # pragma pylint: disable=no-member
    # pragma pylint: disable=import-error
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

def api_method(authenticated=True):
    """ Decorator used to make a method in a model an API method.

    This denotes it as callable through the REST API.
    """

    def _real_api_method(func):
        """ Real decorator to mark a method as runnable by the REST API. """
        func.is_api_method = True
        func.authenticated = authenticated
        return func

    return _real_api_method

# Find out what MIME magic module is in use
# pragma pylint: disable=no-member
if "MIME" in vars(magic):
    # libmagic bindings
    _MS = magic.open(magic.MIME)
    _MS.load()
    def guess_mime_type(data):
        """ Guess a MIME type from magic bytes in a data stream. """
        return _MS.buffer(data)
else:
    # python-magic
    def guess_mime_type(data):
        """ Guess a MIME type from magic bytes in a data stream. """
        return magic.from_buffer(data)
