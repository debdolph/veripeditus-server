/*
 * veripeditus-web - Web frontend to the veripeditus server
 * Copyright (C) 2016  Dominik George <nik@naturalnet.de>
 * Copyright (C) 2016  Eike Tim Jesinghaus <eike@naturalnet.de>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

MapController = function() {
    var self = this;

    // Set up map view
    self.map = L.map("map", {
        zoomControl: false,
        worldCopyJump: true
    });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(self.map);

    // Add debugging handlers if debugging is enabled
    if (Veripeditus.debug) {
        self.map.on('click', function (event) {
            if (event.originalEvent.ctrlKey) {
                fake_pos = {
                    "timestamp": Date.now(),
                    "coords": {
                        "latitude": event.latlng.lat,
                        "longitude": event.latlng.lng,
                        "accuracy": 1
                    }
                };
                Device.onLocationUpdate(fake_pos);
            }
        });
    }

    // Add initial marker for own position
    self.marker_self = L.marker([Device.position.coords.latitude, Device.position.coords.longitude]);
//    self.marker_self.addTo(self.map);
    self.circle_self = L.circle(self.marker_self.getLatLng(), 0);
    self.circle_self.addTo(self.map);

    // Initially center map view to own position
    self.map.setView(self.marker_self.getLatLng(), 16);

    // Already created markers for gameobjects will be stored here.
    self.gameobject_markers = {};

    // Called by GameDataService on gameobjects update
    self.onUpdatedGameObjects = function() {
        // Iterate over gameobjects and add map markers
        $.each(GameData.gameobjects, function (id, gameobject) {
            // Check whether item should be shown on the map
            if (! gameobject.attributes.isonmap) {
                return;
            }

            // Skip if object is own player
            if (id == GameData.current_player_id) {
                return;
            }

            // Look for already created marker for self gameobject id
            var marker = self.gameobject_markers[gameobject.id];
            if (marker) {
                // Marker exists, store location
                marker.setLatLng([gameobject.attributes.latitude, gameobject.attributes.longitude]);
            } else {
                // Marker does not exist
                // Construct marker icon from gameobject image
                var icon = L.icon({
                    'iconUrl': '/api/v2/gameobject/' + gameobject.id + '/image_raw',
                    'iconSize': [32, 32],
                });

                // Create marker at gameobject location
                marker = L.marker([gameobject.attributes.latitude, gameobject.attributes.longitude], {
                    'icon': icon
                });

                // Create popup
                var html = "<h1>" + gameobject.attributes.name + "</h1>";
                html += "<p class='map_popup_image'><img src='/api/v2/gameobject/" + gameobject.id + "/image_raw' /></p>";
                if (gameobject.attributes.gameobject_type == "gameobject_item") {
                    // FIXME also check for collectible
                    html += "<button class='map_popup_button' onClick='MapView.item_collect(" + gameobject.id + ")'>Collect</button>";
                }
                if (gameobject.attributes.gameobject_type == "gameobject_npc") {
                    // FIXME also check for talkable
                    html += "<button class='map_popup_button' onClick='MapView.npc_talk(" + gameobject.id + ")'>Talk</button>";
                }
                marker.bindPopup(html);

                // Add marker to map and store to known markers
                marker.addTo(self.map);
                self.gameobject_markers[gameobject.id] = marker;
            }
        });

        // Iterate over found markers and remove everything not found in gameobjects
        $.each(self.gameobject_markers, function (id, marker) {
            if ($.inArray(id, Object.keys(GameData.gameobjects)) == -1) {
                // Remove marker if object vanished from gameobjects
                self.map.removeLayer(marker);
                delete self.gameobject_markers[id];
            } else if (! GameData.gameobjects[id].attributes.isonmap) {
                // Remove marker if object is not visible on map anymore
                self.map.removeLayer(marker);
                delete self.gameobject_markers[id];
            }
        });
    };

    // Called by DeviceService on geolocation update
    self.onGeolocationChanged = function() {
        // Update position of own marker
        self.marker_self.setLatLng([Device.position.coords.latitude, Device.position.coords.longitude]);

        // Update accuracy radius around own marker
        self.circle_self.setLatLng(self.marker_self.getLatLng());
        self.circle_self.setRadius(Device.position.coords.accuracy);

        // Center map at own marker
        self.map.setView(self.marker_self.getLatLng());
    };

    // Subscribe to event on change of map view
    self.map.on('moveend', function(event) {
        // Update view bounds in GameDataService
        var bounds = event.target.getBounds();
        GameData.setBounds([bounds.getSouth(), bounds.getWest()], [bounds.getNorth(), bounds.getEast()]);
    });

    // Initially set bounds in GameDataService
    var bounds = self.map.getBounds();
    GameData.setBounds([bounds.getSouth(), bounds.getWest()], [bounds.getNorth(), bounds.getEast()]);

    // Pass item_collect to GameData with self reference
    self.item_collect = function (id) {
        GameData.item_collect(id, self);
    };

    // Pass npc_talk to GameData with self reference
    self.npc_talk = function (id) {
        GameData.npc_talk(id, self);
    };

    // Called by GameData routines to close the popup something was called from.
    self.onGameObjectActionDone = function (data) {
        self.map.closePopup();

        // Show any message as a dialog
        // FIXME come up with something prettyer
        if (data.message) {
            var dialog = $('div#dialog');
            dialog.empty();
            dialog.attr("title", GameData.gameobjects[data.gameobject].name);
            var html = "<p>" + data.message + "</p>";
            var elem = $(html);
            dialog.append(elem);
            dialog.dialog();
        }
    };
};

// Instantiate controller and register to services
MapView = new MapController();
Veripeditus.registerView(MapView);
