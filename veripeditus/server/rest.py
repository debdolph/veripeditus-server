"""
API endpoint definitions
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

from flask import g, make_response, redirect
from flask_restless import APIManager, url_for
from werkzeug.wrappers import Response

from veripeditus.server.app import APP, DB
from veripeditus.server.control import needs_authentication
from veripeditus.server.model import *
from veripeditus.server.util import guess_mime_type

_INCLUDE = ['id', 'uuid', 'created', 'updated']

MANAGER = APIManager(APP, flask_sqlalchemy_db=DB)

MANAGER.create_api(User)
MANAGER.create_api(Game)
MANAGER.create_api(World)

# Create APIs for all GameObjects
for go in [GameObject] + GameObject.__subclasses__():
    for rgo in [go] + go.__subclasses__():
        MANAGER.create_api(rgo)

@APP.route("/api/v2/<string:type_>/<int:id_>/<string:method>")
@APP.route("/api/v2/<string:type_>/<int:id_>/<string:method>/<arg>")
def _get_gameobject_method_result(type_, id_, method, arg=None):
    """ Runs method on the object defined by the id and returns it verbatim
    if the object was found and has the method, or 404 if not.
    """

    # Determine tpye of object and object
    types = {"gameobject": GameObject,
             "world": World,
             "game": Game}
    if type_ in types:
        obj = types[type_].query.get(id_)
    else:
        obj = None

    # Check for existence and method existence
    if obj is not None and getattr(obj, method):
        # Get method object
        method_impl = getattr(obj, method)

        # Check whether execution is allowed
        if method_impl.is_api_method:
            # Check authentication
            if method_impl.authenticated and g.user is None:
                return needs_authentication()

            # Run method
            if arg is None:
                ret = method_impl()
            else:
                ret = method_impl(arg)

            if isinstance(ret, Response):
                # We got a complete Response object
                res = ret
            elif isinstance(ret, tuple):
                # We got a tuple of type and data
                res = make_response(ret[1])
                res.headers["Content-Type"] = ret[0]
            else:
                # We need to guess the MIME type
                res = make_response(ret)
                res.headers["Content-Type"] = guess_mime_type(ret)
        else:
            # Return 403 Forbidden
            # FIXME more specific error
            res = ("", 403)
    else:
        # Return 404 Not Found
        # FIXME more specific error
        res = ("", 404)

    return res

@APP.route("/api/v2/gameobject_player/self")
def _get_own_player():
    if g.user is None:
        # Return 404 Not Found
        # FIXME more specific error
        return ("", 404)

    if g.user.current_player is None:
        if g.user.players.count() > 0:
            # Set current player to the first available player of the current user
            g.user.current_player = g.user.players[0]
        else:
            # Create a new player in the first world found
            World.query.filter_by(enabled=True).first().player_join()

    return redirect(url_for(g.user.current_player.__class__, resource_id=g.user.current_player.id))
