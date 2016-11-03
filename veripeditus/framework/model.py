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

from collections import Sequence
from numbers import Real

from flask import g, redirect
from sqlalchemy import and_ as sa_and
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.collections import attribute_mapped_collection

from veripeditus.framework.util import add, get_image_path, get_gameobject_distance, randfloat, send_action
from veripeditus.server.app import DB, OA
from veripeditus.server.model import Base, World
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

    osm_element_id = DB.Column(DB.Integer(), DB.ForeignKey("osm_elements.id"))
    osm_element = DB.relationship(OA.element, backref=DB.backref("osm_elements",
                                                                 lazy="dynamic"),
                                  foreign_keys=[osm_element_id])

    type = DB.Column(DB.Unicode(256))

    attributes = association_proxy("gameobjects_to_attributes", "value",
                                   creator=lambda k, v: GameObjectsToAttributes(
                                       attribute=Attribute(key=k, value=v)))

    def gameobject_type(self):
        return self.__tablename__

    def distance_to(obj):
        return get_gameobject_distance(self, obj)

    @property
    def image_path(self):
        return get_image_path(self.world.game.module, self.image)

    @api_method
    def image_raw(self):
        with open(self.image_path, "rb") as file:
            return file.read()

    @classmethod
    def spawn(cls, world=None):
        if world is None:
            # Iterate over all defined GameObject classes
            for go in cls.__subclasses__():
                # Iterate over all worlds using the game
                worlds = World.query.filter(World.game.has(package=go.__module__.split(".")[2])).all()
                for world in worlds:
                    if "spawn" in vars(go):
                        # Call spawn for each world
                        go.spawn(world)
                    else:
                        # Call parameterised default spawn code
                        go.spawn_default(world)

    @classmethod
    def spawn_default(cls, world):
        # Get current player
        current_player = None if g.user is None else g.user.current_player

        # Determine spawn location
        if "spawn_latlon" in vars(cls):
            latlon = cls.spawn_latlon

            if isinstance(latlon, Sequence):
                # We got one of:
                #  (lat, lon)
                #  ((lat, lon), (lat, lon))
                #  ((lat, lon), radius)
                if isinstance(latlon[0], Sequence) and isinstance(latlon[1], Sequence):
                    # We got a rect like ((lat, lon), (lat, lon))
                    # Randomise coordinates within that rect
                    latlon = (randfloat(latlon[0][0], latlon[1][0]), randfloat(latlon[0][1], latlon[1][1]))
                elif isinstance(latlon[0], Sequence) and isinstance(latlon[1], Real):
                    # We got a circle like ((lat, lon), radius)
                    # FIXME implement
                    raise RuntimeError("Not implemented.")
                elif isinstance(latlon[0], Real) and isinstance(latlon[1], Real):
                    # We got a single point like (lat, lon)
                    # Nothing to do, we can use that as is
                    pass
                else:
                    raise TypeError("Unknown value for spawn_latlon.")

            # Define a single spawn point with no linked OSM element
            spawn_points = {latlon: None}
        elif "spawn_osm" in vars(cls):
            # Skip if no current player or current player not in this world
            if current_player is None or current_player.world is not world:
                return

            # Define bounding box around current player
            # FIXME do something more intelligent here
            lat_min = current_player.latitude - 0.001
            lat_max = current_player.latitude + 0.001
            lon_min = current_player.longitude - 0.001
            lon_max = current_player.longitude + 0.001
            bbox_queries = [OA.node.latitude>lat_min, OA.node.latitude<lat_max,
                            OA.node.longitude>lon_min, OA.node.longitude<lon_max]

            # Build list of tag values using OSMAlchemy
            has_queries = [OA.node.tags.any(key=k, value=v) for k, v in cls.spawn_osm.items()]
            and_query = sa_and(*bbox_queries, *has_queries)

            # Do query
            # FIXME support more than plain nodes
            nodes = DB.session.query(OA.node).filter(and_query).all()

            # Extract latitude and longitude information and build spawn_points
            latlons = [(node.latitude, node.longitude) for node in nodes]
            spawn_points = dict(zip(latlons, nodes))
        else:
            # Do nothing if we cannot determine a location
            return

        for latlon, osm_element in spawn_points.items():
            # Determine existing number of objects on map
            existing = cls.query.filter_by(world=world, isonmap=True, osm_element=osm_element).count()
            if "spawn_min" in vars(cls) and "spawn_max" in vars(cls) and existing < cls.spawn_min:
                to_spawn = cls.spawn_max - existing
            elif existing == 0:
                to_spawn = 1
            else:
                to_spawn = 0

            # Spawn the determined number of objects
            for i in range(0, to_spawn):
                # Create a new object
                obj = cls()
                obj.world = world
                obj.latitude = latlon[0]
                obj.longitude = latlon[1]
                obj.osm_element = osm_element

                # Determine any defaults
                for k in vars(cls):
                    if k.startswith("default_"):
                        setattr(obj, k[8:], getattr(cls, k))

                # Add to session
                add(obj)

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
        GameObject.__init__(self, **kwargs)
        if "image" not in kwargs:
            self.image = "avatar_default"

    def may_accept_handover(self, item):
        return True

    @api_method
    def update_position(self, latlon):
        if g.user is None:
            # FIXME proper error
            return None

        # Only the own position may be updated
        if g.user is not self.user:
            # FIXME proper error
            return None

        # Update position
        self.latitude, self.longitude = [float(x) for x in latlon.split(",")]
        DB.session.add(self)
        DB.session.commit()

        # Redirect to own object
        return redirect("/api/gameobject_player/%i" % self.id)

    @classmethod
    def spawn_default(cls, world):
        pass

class Item(GameObject):
    __tablename__ = "gameobject_item"

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)

    owner_id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject_player.id"))
    owner = DB.relationship("veripeditus.framework.model.Player", backref=DB.backref("inventory", lazy="dynamic"),
                            foreign_keys=[owner_id])

    collectible = True
    collectible_max_distance = None
    handoverable = True

    @api_method
    def collect(self):
        if g.user is not None and g.user.current_player is not None:
            player = g.user.current_player
        else:
            # FIXME throw proper error
            return None

        if self.collectible_max_distance is not None:
            if self.collectible_max_distance > self.distance_to(player):
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

    def say(self, message):
        return send_action("say", self, message)
