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
import random

from flask import g, redirect
from flask_restless import url_for
from sqlalchemy import and_ as sa_and
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.sql import and_

from veripeditus.framework.util import get_image_path, get_gameobject_distance, random_point_in_polygon, send_action
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

    _api_includes = ["world", "attributes"]

    id = DB.Column(DB.Integer(), primary_key=True)

    # Columns and relationships

    name = DB.Column(DB.String(32))
    image = DB.Column(DB.String(32), default="dummy", nullable=False)

    world_id = DB.Column(DB.Integer(), DB.ForeignKey("world.id"))
    world = DB.relationship("World", backref=DB.backref("gameobjects",
                                                        lazy="dynamic"),
                            foreign_keys=[world_id])

    longitude = DB.Column(DB.Float(), default=0.0, nullable=False)
    latitude = DB.Column(DB.Float(), default=0.0, nullable=False)

    osm_element_id = DB.Column(DB.Integer(), DB.ForeignKey("osm_elements.id"))
    osm_element = DB.relationship(OA.element, backref=DB.backref("osm_elements",
                                                                 lazy="dynamic"),
                                  foreign_keys=[osm_element_id])

    type = DB.Column(DB.Unicode(256))

    attributes = association_proxy("gameobjects_to_attributes", "value",
                                   creator=lambda k, v: GameObjectsToAttributes(
                                       attribute=Attribute(key=k, value=v)))

    distance_max = None

    @property
    def gameobject_type(self):
        # Return type of gameobject
        return self.__tablename__

    def distance_to(self, obj):
        # Return distance to another gamobject
        return get_gameobject_distance(self, obj)

    @property
    def image_path(self):
        # Return path of image file
        return get_image_path(self.world.game.module, self.image)

    @hybrid_property
    def isonmap(self):
        return True

    @property
    def distance_to_current_player(self):
        # Return distance to current player
        if g.user is None or g.user.current_player is None:
            return None
        return self.distance_to(g.user.current_player)

    @api_method(authenticated=False)
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
                #  ((lat, lon), (lat, lon),…)
                #  ((lat, lon), radius)
                if isinstance(latlon[0], Sequence) and isinstance(latlon[1], Sequence):
                    if len(latlon) == 2:
                        # We got a rect like ((lat, lon), (lat, lon))
                        # Randomise coordinates within that rect
                        latlon = (random.uniform(latlon[0][0], latlon[1][0]), random.uniform(latlon[0][1], latlon[1][1]))
                    else:
                        # We got a polygon, randomise coordinates within it
                        latlon = random_point_in_polygon(latlon)
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
            existing = cls.query.filter_by(world=world, osm_element=osm_element, isonmap=True).count()
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

                # Derive missing defaults from class name
                if obj.image is None:
                    obj.image = cls.__name__.lower()
                if obj.name is None:
                    obj.name = cls.__name__.lower()

                # Add to session
                obj.commit()

    def commit(self):
        """ Commit this object to the database. """

        DB.session.add(self)
        DB.session.commit()

class GameObjectsToAttributes(Base):
    __tablename__ = "gameobjects_to_attributes"

    gameobject_id = DB.Column(DB.Integer(),
                              DB.ForeignKey('gameobject.id'))
    attribute_id = DB.Column(DB.Integer(),
                             DB.ForeignKey('attribute.id'))

    gameobject = DB.relationship(GameObject, foreign_keys=[gameobject_id],
                                 backref=DB.backref("attributes",
                                                    collection_class=attribute_mapped_collection(
                                                        "key"),
                                                    cascade="all, delete-orphan"))

    attribute = DB.relationship(Attribute, foreign_keys=[attribute_id])
    key = association_proxy("attribute", "key")
    value = association_proxy("attribute", "value")

class Player(GameObject):
    __tablename__ = "gameobject_player"

    _api_includes = GameObject._api_includes + ["inventory"]

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)

    # Relationship to the user which the player belongs to
    user_id = DB.Column(DB.Integer(), DB.ForeignKey("user.id"))
    user = DB.relationship("User", backref=DB.backref("players",
                                                      lazy="dynamic"),
                           foreign_keys=[user_id])

    def __init__(self, **kwargs):
        GameObject.__init__(self, **kwargs)
        if "image" not in kwargs:
            self.image = "avatar_default"

    def new_item(self, itemclass):
        item = itemclass()
        item.world = self.world
        item.owner = self

        # Determine any defaults
        for k in vars(itemclass):
            if k.startswith("default_"):
                setattr(item, k[8:], getattr(itemclass, k))

        # Derive missing defaults from class name
        if item.image is None:
            item.image = itemclass.__name__.lower()
        if item.name is None:
            item.name = itemclass.__name__.lower()

        DB.session.add(item)
        DB.session.add(self)
        DB.session.commit()

    def has_item(self, itemclass):
        # Return how many items of the class the player has
        count = 0
        for item in self.inventory:
            if isinstance(item, itemclass):
                count += 1
        return count

    def has_items(self, *itemclasses):
        # Return whether the player has every given item at least one time
        for itemclass in itemclasses:
            if not self.has_item(itemclass):
                return False

        return True

    def drop_item(self, itemclass):
        # Remove every item on a class from the players inventory
        for item in self.inventory:
            if isinstance(item, itemclass):
                DB.session.delete(item)
                DB.session.commit()

    def drop_items(self, *itemclasses):
        # Remove every item of every given class from the players inventory
        for itemclass in itemclasses:
            self.drop_item(itemclass)

    def may_accept_handover(self, item):
        return True

    @api_method(authenticated=True)
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

        # FIXME remove slow iteration
        for item in Item.query.filter_by(world=g.user.current_player.world).all():
            if item.auto_collect_radius > 0 and item.distance_to_current_player <= item.auto_collect_radius:
                item.collect()

        DB.session.add(self)
        DB.session.commit()

        # Redirect to own object
        return redirect(url_for(self.__class__, resource_id=self.id))

    @classmethod
    def spawn_default(cls, world):
        pass

    @hybrid_property
    def isonmap(self):
        # Check if isonmap is called by the class or by an instance
        if isinstance(self, type):
            cls = self
        else:
            cls = self.__class__

        if g.user is not None and g.user.current_player is not None:
            # Check if specific constants are set and apply their effects
            mod = g.user.current_player.world.game.module
            if hasattr(mod, "VISIBLE_RAD_PLAYERS"):
                # Check if the player is in the visible range
                if self is not cls and self.distance_to_current_player > mod.VISIBLE_RAD_PLAYERS:
                    return False
            if hasattr(mod, "HIDE_SELF"):
                # Hide the player if it is the current player
                if self is not cls and self == g.user.current_player and mod.HIDE_SELF:
                    return False
        return True

class Item(GameObject):
    __tablename__ = "gameobject_item"

    # Columns

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)

    owner_id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject_player.id"))
    owner = DB.relationship("veripeditus.framework.model.Player", backref=DB.backref("inventory", lazy="dynamic"),
                            foreign_keys=[owner_id])

    # Class attributes

    collectible = True
    handoverable = True
    owned_max = None
    auto_collect_radius = 0
    show_if_owned_max = None

    @api_method(authenticated=True)
    def collect(self):
        if g.user is not None and g.user.current_player is not None:
            player = g.user.current_player
        else:
            # FIXME throw proper error
            return None

        # Check if the player is in range
        if self.distance_max is not None:
            if self.distance_max < self.distance_to(player):
                return send_action("notice", self, "You are too far away!")

        # Check if the player already has the maximum amount of items of a class
        if self.owned_max is not None:
            if player.has_item(self.__class__) >= self.owned_max:
                return send_action("notice", self, "You have already collected enough of this!")

        # Check if the collection is allowed
        if self.collectible and self.isonmap and self.may_collect(player):
            # Change owner
            self.owner = player
            self.on_collected()
            DB.session.add(self)
            DB.session.commit()
            return redirect(url_for(self.__class__, resource_id=self.id))
        else:
            return send_action("notice", self, "You cannot collect this!")

    @api_method(authenticated=True)
    def handover(self, target_player):
        # Check if the handover is allowed
        if self.owner is not None and self.handoverable and self.may_handover(target_player) and target_player.may_accept_handover(self):
            # Change owner
            self.owner = target_player
            self.on_handedover()
            DB.session.add(self)
            DB.session.commit()
            return redirect(url_for(self.__class__, resource_id=self.id))
        else:
            return send_action("notice", self, "You cannot hand this over.")

    @hybrid_property
    def isonmap(self):
        # Check whether we were called as class or instance method
        if isinstance(self, type):
            # Class method
            cls = self
        else:
            cls = self.__class__

        # Seed expression
        expr = True

        # Check if item is owned by someone
        if self is cls:
            # For class method, and_() existing expression with check for ownership
            expr = and_(expr, self.owner==None)
        elif self.owner is not None:
            # For instance method, return a terminal False if owned by someone
            return False

        # Check for owned_max functionality
        # Independent of class or instance method
        if g.user is not None and g.user.current_player is not None:
            if self.owned_max is not None and g.user.current_player.has_item(cls) >= self.owned_max:
                if self.show_if_owned_max is None or not self.show_if_owned_max:
                    # Return a terminal false
                    return False
            mod = g.user.current_player.world.game.module
            if hasattr(mod, "VISIBLE_RAD_ITEMS"):
                if self is not cls and self.distance_to_current_player > mod.VISIBLE_RAD_ITEMS:
                    return False

        # Verify conditional attributes for spawning
        # Independent of class or instance method
        if hasattr(self, "spawn_player_attributes"):
            for key, value in self.spawn_player_attributes.items():
                if key in g.user.current_player.attributes:
                    attribute = g.user.current_player.attributes[key]
                else:
                    return False

                if value is not None and attribute != value:
                    return False

        # Find out final return value
        if self is cls:
            # For class method, return boolean SQL expression
            return expr
        else:
            # For instance method, return terminal True
            return True

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

    # Columns

    id = DB.Column(DB.Integer(), DB.ForeignKey("gameobject.id"), primary_key=True)

    # Attribute for determining if a player can talk to the NPC
    talkable = True

    def say(self, message):
        return send_action("say", self, message)

    def on_talk(self):
        pass

    @api_method(authenticated=True)
    def talk(self):
        if g.user is not None and g.user.current_player is not None:
            player = g.user.current_player
        else:
            # FIXME throw proper error
            return None

        # Check if the player is in range for talking to the NPC
        if self.distance_max is not None:
            if self.distance_max < self.distance_to(player):
                return send_action("notice", self, "You are too far away!")

        # Check if talking to the NPC is allowed
        if self.talkable and self.isonmap and self.may_talk(player):
            # Run talk logic
            return self.on_talk()
        else:
            return send_action("notice", self, "You cannot talk to this character!")

    def may_talk(self, player):
        return True

    @hybrid_property
    def isonmap(self):
        if isinstance(self, type):
            cls = self
        else:
            cls = self.__class__

        if g.user is not None and g.user.current_player is not None:
            mod = g.user.current_player.world.game.module
            if hasattr(mod, "VISIBLE_RAD_NPCS"):
                if self is not cls and self.distance_to_current_player > mod.VISIBLE_RAD_NPCS:
                    return False

        return True
