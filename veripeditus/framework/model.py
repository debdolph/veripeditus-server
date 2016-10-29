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

from veripeditus.server.app import DB
from veripeditus.server.model import Base

class GameObject(Base):
    __tablename__ = "gameobject"
    
    world_id = DB.Column(DB.Integer(), DB.ForeignKey("world.id"))
    world = DB.relationship("World", backref=DB.backref("players",
                                                        lazy="dynamic"),
                            foreign_keys=[world_id])

    longitude = DB.Column(DB.Float(), default=0.0, nullable=False)
    latitude = DB.Column(DB.Float(), default=0.0, nullable=False)

    type_ = DB.Column(DB.Unicode(256))

    __mapper_args__ = {
                       "polymorphic_identity": "gameobject",
                       "polymorphic_on": type_
                      }

class Player(GameObject):
    __tablename__ = "gameobject_player"
    
    name = DB.Column(DB.String(32), unique=True, nullable=False)
    avatar = DB.Column(DB.String(32), default="default", nullable=False)

    user_id = DB.Column(DB.Integer(), DB.ForeignKey("user.id"))
    user = DB.relationship("User", backref=DB.backref("players",
                                                      lazy="dynamic"),
                           foreign_keys=[user_id])

    __mapper_args__ = {
                       "polymorphic_identity": "player"
                      }
