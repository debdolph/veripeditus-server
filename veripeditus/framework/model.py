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

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection

class _GameObjectMeta(type(Base)):
    """ Meta-class to allow generation of dynamic mapper args.

    Necessary because SQLAlchemy traverses __dict__ to find configuration
    attributes, and our inherited classes in games obviously don't get
    inherited __mapper_args__ in their __dict__. This method injects
    the dictionary to the __dict__ upon instantiation as meta-class.
    """

    def __new__(cls, *args, **kwargs):
        obj = type(Base).__new__(cls, *args, **kwargs)

        mapperargs = {}

        if obj.__module__ == "veripeditus.framework.model":
            # We are a parent class in the framework
            mapperargs["polymorphic_on"] = obj.type
            mapperargs["with_polymorphic"] = "*"
            mapperargs["polymorphic_identity"] = obj.__name__
        elif obj.__module__.startswith("veripeditus.game"):
            # We are an implementation in a game
            mapperargs["polymorphic_identity"] = \
                "game_%s_%s" % (obj.__module__.split(".")[2], obj.__name__)
        else:
            raise RuntimeError("GameObject can only be derived in game modules.")

        # Inject into class
        setattr(obj, "__mapper_args__", mapperargs)
        return obj

class Attribute(Base):
    # Key/value pair
    key = DB.Column(DB.Unicode(256))
    value = DB.Column(DB.Unicode(256))

class GameObject(Base, metaclass=_GameObjectMeta):
    __tablename__ = "gameobject"

    id = DB.Column(DB.Integer(), primary_key=True)
    
    world_id = DB.Column(DB.Integer(), DB.ForeignKey("world.id"))
    world = DB.relationship("World", backref=DB.backref("gameobjects",
                                                        lazy="dynamic"),
                            foreign_keys=[world_id])

    longitude = DB.Column(DB.Float(), default=0.0, nullable=False)
    latitude = DB.Column(DB.Float(), default=0.0, nullable=False)

    type = DB.Column(DB.Unicode(256))

    attributes = association_proxy("gameobjects_to_attributes", "value",
                                 creator=lambda k, v: GameObjectsToAttributes(attribute=Attribute(key=k, value=v)))

class GameObjectsToAttributes(Base):
    __tablename__ = "gameobjects_to_attributes"

    gameobject_id = DB.Column(DB.Integer(),
                              DB.ForeignKey('gameobject.id'))
    attribute_id = DB.Column(DB.Integer(),
                             DB.ForeignKey('attribute.id'))

    gameobject = DB.relationship(GameObject, foreign_keys=[gameobject_id],
                                backref=DB.backref("gameobjects_to_attributes",
                                                   collection_class=attribute_mapped_collection(
                                                       "key"
                                                   ), cascade="all, delete-orphan"))

    attribute = DB.relationship(Attribute, foreign_keys=[attribute_id])
    key = association_proxy("attribute", "key")
    value = association_proxy("attribute", "value")

class Player(GameObject):
    __tablename__ = "gameobject_player"

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)
    
    name = DB.Column(DB.String(32), unique=True, nullable=False)
    avatar = DB.Column(DB.String(32), default="default", nullable=False)

    user_id = DB.Column(DB.Integer(), DB.ForeignKey("user.id"))
    user = DB.relationship("User", backref=DB.backref("players",
                                                      lazy="dynamic"),
                           foreign_keys=[user_id])

class Item(GameObject):
    __tablename__ = "gameobject_item"

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)

    owner_id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject_player.id"))
    owner = DB.relationship("Player", backref=DB.backref("inventory", lazy="dynamic"), foreign_keys=[owner_id])

class NPC(GameObject):
    __tablename__ = "gameobject_npc"

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)

    name = DB.Column(DB.String(32), nullable=False)
