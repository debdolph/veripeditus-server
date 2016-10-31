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

from flask import g, redirect
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection

from veripeditus.framework.util import get_image_path
from veripeditus.server.app import DB
from veripeditus.server.model import Base
from veripeditus.server.util import api_method

class _GameObjectMeta(type(Base)):
    """ Meta-class to allow generation of dynamic mapper args.

    Necessary because SQLAlchemy traverses __dict__ to find configuration
    attributes, and our inherited classes in games obviously don't get
    inherited __mapper_args__ in their __dict__. This method injects
    the dictionary to the __dict__ upon instantiation as meta-class.
    """

    def __new__(cls, *args, **kwargs):
        """ Called upon deriving from GameObject, which uses this meta-class. """

        # Create a new instance by calling __new__ on our parent class,
        # which is the meta-class of the used SQLAlchemy declarative base
        obj = super().__new__(cls, *args, **kwargs)

        # Later filled with the relevant mapper args
        mapperargs = {}

        if obj.__module__ == "veripeditus.framework.model":
            # We are a parent class in the framework, so we need to configure
            # the polymorphism to use
            mapperargs["polymorphic_on"] = obj.type
            mapperargs["with_polymorphic"] = "*"
            mapperargs["polymorphic_identity"] = obj.__name__
        elif obj.__module__.startswith("veripeditus.game"):
            # We are an implementation in a game, so we only need to set the identity
            # It is the game module and the class name defined there prefixed with game
            mapperargs["polymorphic_identity"] = \
                "game_%s_%s" % (obj.__module__.split(".")[2], obj.__name__)
        else:
            # We are somwhere else, which is a bug
            raise RuntimeError("GameObject can only be derived in game modules.")

        # Inject into class and return the new instance
        setattr(obj, "__mapper_args__", mapperargs)
        return obj

class Attribute(Base):
    # Key/value pair
    key = DB.Column(DB.Unicode(256))
    value = DB.Column(DB.Unicode(256))

class GameObject(Base, metaclass=_GameObjectMeta):
    __tablename__ = "gameobject"

    id = DB.Column(DB.Integer(), primary_key=True)

    image = DB.Column(DB.String(32), default="dummy", nullable=False)

    world_id = DB.Column(DB.Integer(), DB.ForeignKey("world.id"))
    world = DB.relationship("World", backref=DB.backref("gameobjects",
                                                        lazy="dynamic"),
                            foreign_keys=[world_id])

    longitude = DB.Column(DB.Float(), default=0.0, nullable=False)
    latitude = DB.Column(DB.Float(), default=0.0, nullable=False)
    isonmap = DB.Column(DB.Boolean(), default=True, nullable=False)

    type = DB.Column(DB.Unicode(256))

    attributes = association_proxy("gameobjects_to_attributes", "value",
                                   creator=lambda k, v: GameObjectsToAttributes(
                                       attribute=Attribute(key=k, value=v)))

    def gameobject_type(self):
        return self.__tablename__

    @property
    def image_path(self):
        return get_image_path(self.world.game.module, self.image)

    @api_method
    def image_raw(self):
        with open(self.image_path, "rb") as file:
            return file.read()

class GameObjectsToAttributes(Base):
    __tablename__ = "gameobjects_to_attributes"

    gameobject_id = DB.Column(DB.Integer(),
                              DB.ForeignKey('gameobject.id'))
    attribute_id = DB.Column(DB.Integer(),
                             DB.ForeignKey('attribute.id'))

    gameobject = DB.relationship(GameObject, foreign_keys=[gameobject_id],
                                 backref=DB.backref("gameobjects_to_attributes",
                                                    collection_class=attribute_mapped_collection(
                                                        "key"),
                                                    cascade="all, delete-orphan"))

    attribute = DB.relationship(Attribute, foreign_keys=[attribute_id])
    key = association_proxy("attribute", "key")
    value = association_proxy("attribute", "value")

class Player(GameObject):
    __tablename__ = "gameobject_player"

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)

    name = DB.Column(DB.String(32), unique=True, nullable=False)

    user_id = DB.Column(DB.Integer(), DB.ForeignKey("user.id"))
    user = DB.relationship("User", backref=DB.backref("players",
                                                      lazy="dynamic"),
                           foreign_keys=[user_id])

    api_exclude = ["user.password"]

    def __init__(self, **kwargs):
        super().__init__(self, **kwargs)
        if "image" not in kwargs:
            self.image = "avatar_default"

    def may_accept_handover(self, item):
        return True

class Item(GameObject):
    __tablename__ = "gameobject_item"

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)

    owner_id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject_player.id"))
    owner = DB.relationship("Player", backref=DB.backref("inventory", lazy="dynamic"),
                            foreign_keys=[owner_id])

    collectible = True
    handoverable = True

    @api_method
    def collect(self):
        if g.user is not None and g.user.current_player is not None:
            player = g.user.current_player
        else:
            # FIXME throw proper error
            return None

        if self.collectible and self.isonmap and self.may_collect(player):
            self.owner = player
            self.isonmap = False
            self.on_collected()
            DB.session.add(self)
            DB.session.commit()
            return redirect("/api/gameobject_item/%i" % self.id)
        else:
            # FIXME throw proper error
            return None

    @api_method
    def handover(self, target_player):
        if self.owner is not None and self.handoverable and self.may_handover(target_player) and target_player.may_accept_handover(self):
            self.owner = target_player
            self.on_handedover()
            DB.session.add(self)
            DB.session.commit()
            return redirect("/api/gameobject_item/%i" % self.id)
        else:
            # FIXME throw proper error
            return None

    def may_collect(self, player):
        return True

    def may_handover(self, player):
        return True

    def on_collected(self):
        pass

    def on_handedover(self):
        pass

class NPC(GameObject):
    __tablename__ = "gameobject_npc"

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)

    name = DB.Column(DB.String(32), nullable=False)
