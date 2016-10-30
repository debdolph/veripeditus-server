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

from flask import make_response
from flask_restless import APIManager
from veripeditus.server.app import APP, DB
from veripeditus.server.model import *
from veripeditus.server.util import guess_mime_type

# Global includes for all collections
_INCLUDE = ['id', 'uuid', 'created', 'updated']

_METHODS = ['GET_MANY', 'GET_SINGLE', 'PATCH_MANY', 'PATCH_SINGLE',
            'DELETE_MANY', 'DELETE_SINGLE', 'POST']

MANAGER = APIManager(APP, flask_sqlalchemy_db=DB)

MANAGER.create_api(User,
                   include_columns=_INCLUDE+['username', 'email', 'players',
                   'players.name', 'players.longitude', 'players.latitude',
                   'players.avatar'],
                   methods=['GET', 'POST', 'DELETE', 'PATCH', 'PUT'])


MANAGER.create_api(Game, include_columns=_INCLUDE+['package', 'name', 'version',
                                                   'description', 'author',
                                                   'license'],
                   methods=['GET'])

MANAGER.create_api(World, include_columns=_INCLUDE+['name', 'game'],
                   methods=['GET'])

# Create APIs for all GameObjects
for go in [GameObject] + GameObject.__subclasses__():
    MANAGER.create_api(go,
                       include_methods=["gameobject_type"],
                       exclude_columns=go.api_exclude,
                       methods=['GET', 'POST', 'DELETE', 'PATCH', 'PUT'])

@APP.route("/api/gameobject/<int:id_>/<string:method>")
def _get_gameobject_method_result(id_, method):
    """ Runs method on the object defined by the id and returns it verbatim
    if the object was found and has the method, or 404 if not.
    """

    # Get the GameObject
    go = GameObject.query.get(id_)

    # Check for existence and method existence
    if go is not None and getattr(go, method):
        # Get method object
        m = getattr(go, method)

        # Check whether execution is allowed
        if m.is_api_method:
            # Return method result verbatim
            ret = m()
            if isinstance(ret, tuple):
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
