# veripeditus-server - Server component for the Veripeditus game framework
# Copyright (C) 2015  Dominik George <nik@naturalnet.de>
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

"""
Module containing base classes for all kinds of game objects.
"""

from veripeditus.framework.gameobject import GameObject

class Item(GameObject):
    """
    A generic object that is shown on the game map and that
    can be interacted with; otherwise immutable.
    """

    pass
