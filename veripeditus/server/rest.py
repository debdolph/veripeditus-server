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

from flask_restless import APIManager
from veripeditus.server.app import APP, DB
from veripeditus.server.model import *

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
    MANAGER.create_api(go, exclude_columns=go.api_exclude,
                       methods=['GET', 'POST', 'DELETE', 'PATCH', 'PUT'])
