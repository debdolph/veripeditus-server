# veripeditus-server - Server component for the Veripeditus game framework
# Copyright (C) 2017  Dominik George <nik@naturalnet.de>
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

# Directories for live games and working trees
DIR_LIVE = os.path.join(APP.config['CODE_EDITOR_PATH'], 'live')
DIR_WORK = os.path.join(APP.config['CODE_EDITOR_PATH'], 'work')

# Create missing directories
if not os.path.isdir(DIR_LIVE):
    os.mkdir(DIR_LIVE)
f not os.path.isdir(DIR_WORK):
    os.mkdir(DIR_WORK)

# Append live directory to module path
sys.path.append(DIR_LIVE)
