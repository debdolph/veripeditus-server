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

from flask.ext.restless import APIManager
from veripeditus.server.app import app
from veripeditus.server.control import get_server_info
from veripeditus.server.model import *

# Global includes for all collections
_include = ['id', 'uuid', 'created', 'updated']

def _api_add_server_info(*args, **kwargs):
    if "data" in kwargs:
        tbm = kwargs["data"]
    elif "result" in kwargs:
        tbm = kwargs["result"]
    else:
        return

    tbm["server_info"] = get_server_info()

_global_general_post_processors = [_api_add_server_info]
_methods = ['GET_MANY', 'GET_SINGLE', 'PATCH_MANY', 'PATCH_SINGLE', 'DELETE_MANY', 'DELETE_SINGLE', 'POST']
_global_post_processors = {m: _global_general_post_processors for m in _methods}

manager = APIManager(app, flask_sqlalchemy_db=db, postprocessors=_global_post_processors)

manager.create_api(Player, include_columns=_include+['username', 'name', 'email', 'longitude', 'latitude'],
    include_methods=['avatar_base64'], methods=['GET', 'POST', 'DELETE', 'PATCH', 'PUT'])

manager.create_api(Game, include_columns=_include+['package', 'name', 'version',
                                                'description', 'author', 'license'],
    methods=['GET'])
