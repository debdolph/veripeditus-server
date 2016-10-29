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

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)
    
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

    @property
    def __mapper_args__(self):
        class_name = self.__class__.__name__
        module_name = self.__class__.__module__

        if module_name == "veripeditus.framework.model" and class_name == "GameObject":
            return {"polymorphic_on": self.__class__.type_, "with_polymorphic":"*"}
        if module_name == "veripeditus.framework.model":
            return  {"polymorphic_identity": class_name}
        elif module_name.startswith("veripeditus.game"):
            return {"polymorphic_identity": "game_%s_%s" % \
                                            (module_name.split(".")[2], class_name)
                   }

class Player(GameObject):
    __tablename__ = "gameobject_player"
    
    name = DB.Column(DB.String(32), unique=True, nullable=False)
    avatar = DB.Column(DB.String(32), default="default", nullable=False)

    user_id = DB.Column(DB.Integer(), DB.ForeignKey("user.id"))
    user = DB.relationship("User", backref=DB.backref("players",
                                                      lazy="dynamic"),
                           foreign_keys=[user_id])
