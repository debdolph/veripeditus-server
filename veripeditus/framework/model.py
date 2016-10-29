# veripeditus-server - Server component for the Veripeditus game framework
# Copyright (C) 2016  Dominik George <nik@naturalnet.de>
# Copyright (C) 2016  Eike Tim Jesinghaus <eike@naturalnet.de>
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

# FIXME move to proper place
class classproperty(object):
    def __init__(self, getter):
        self.getter= getter
    def __get__(self, instance, owner):
        return self.getter(owner)

class GameObject(Base):
    __tablename__ = "gameobject"

    id = DB.Column(DB.Integer(), primary_key=True)
    
    world_id = DB.Column(DB.Integer(), DB.ForeignKey("world.id"))
    world = DB.relationship("World", backref=DB.backref("gameobjects",
                                                        lazy="dynamic"),
                            foreign_keys=[world_id])

    longitude = DB.Column(DB.Float(), default=0.0, nullable=False)
    latitude = DB.Column(DB.Float(), default=0.0, nullable=False)

    type = DB.Column(DB.Unicode(256))

    @classproperty
    def __mapper_args__(cls):
        class_name = cls.__name__
        module_name = cls.__module__

        mapperargs = {}

        if module_name == "veripeditus.framework.model":
            mapperargs["polymorphic_on"] = cls.type
            mapperargs["with_polymorphic"] = "*"
            mapperargs["polymorphic_identity"] = class_name
        elif module_name.startswith("veripeditus.game"):
            mapperargs["polymorphic_identity"] = \
                "game_%s_%s" % (module_name.split(".")[2], class_name)
        else:
            raise RuntimeError("GameObject can only be derived in game modules.")

        return mapperargs

class Player(GameObject):
    __tablename__ = "gameobject_player"

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)
    
    name = DB.Column(DB.String(32), unique=True, nullable=False)
    avatar = DB.Column(DB.String(32), default="default", nullable=False)

    user_id = DB.Column(DB.Integer(), DB.ForeignKey("user.id"))
    user = DB.relationship("User", backref=DB.backref("players",
                                                      lazy="dynamic"),
                           foreign_keys=[user_id])
