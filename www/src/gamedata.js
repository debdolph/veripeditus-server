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

GameObject = function(id) {
    this.id = id;
    this.latitude = 0.0;
    this.longitude = 0.0;
};

GameDataService = function() {
    var self = this;

    // Status objects
    self.bounds = [
        [0.0, 0.0],
        [0.0, 0.0]];

    // Storage objects
    self.gameobjects = {};
    self.gameobjects_temp = {};
    self.gameobjects_missing = 0;
    self.gameobject_types = ["player", "item", "npc"];

    // Current player id
    self.current_player_id = -1;

    self.doRequest = function (method, url, cb, data) {
        // Fill options here
        var options = {};
        options.method = method;
        options.url = url;
        if (cb) {
            options.dataType = "json";
            options.success = cb;
        }
        if (data) {
            options.dataType = "json";
            options.contentType = "application/json";
            options.data = data;
        }

        // Check whether a username was provided
        if (localStorage.username) {
            // Add username and password
            options.username = localStorage.getItem("username");
            options.password = localStorage.getItem("password");

            // Do the request
            return $.ajax(options);
        } else {
            // Skip request
            return false;
        }
    };

    self.onGeolocationChanged = function() {
        // Update own location on server if logged in
        if (self.current_player_id > -1) {
            // Update location in player object
            self.gameobjects[self.current_player_id].latitude = Device.position.coords.latitude;
            self.gameobjects[self.current_player_id].longitude = Device.position.coords.longitude;

            // Send the update request
            self.doRequest("GET", "/api/gameobject/" + self.current_player_id + "/update_position/" + self.gameobjects[self.current_player_id].latitude + "," + self.gameobjects[self.current_player_id].longitude);
        }
    };

    self.onReturnGameObjects = function(data) {
        // Iterate over data and merge into gameobjects store
        for (var i = 0; i < data.objects.length; i++) {
            var go = data.objects[i];
            self.gameobjects_temp[go.id] = go;
        }

        // Reduce missing objects counter
        self.gameobjects_missing -= 1;

        if (self.gameobjects_missing == 0) {
            // Move gameobjects to working copy
            self.gameobjects = self.gameobjects_temp;
            self.gameobjects_temp = {};

            // Call onUpdatedGameObjects on all views
            for (view of Veripeditus.views) {
                if (view.onUpdatedGameObjects) {
                    view.onUpdatedGameObjects();
                }
            }
        }
    };

    self.updateGameObjects = function() {
        // Skip if gameobjects are still missing from previous load
        if (self.gameobjects_missing > 0) {
            return;
        }

        // Only run if logged-in
        if (self.current_player_id > -1) {
            // Construct JSON query filter for REST API
            var query = {
                'filters': [{
                    'or': [{
                        'and': [{
                            'name': 'latitude',
                            'op': 'ge',
                            'val': self.bounds[0][0]
                        },
                        {
                            'name': 'latitude',
                            'op': 'le',
                            'val': self.bounds[1][0]
                        },
                        {
                            'name': 'longitude',
                            'op': 'ge',
                            'val': self.bounds[0][1]
                        },
                        {
                            'name': 'longitude',
                            'op': 'le',
                            'val': self.bounds[1][1]
                        },
                        {
                            'name': 'world',
                            'op': 'has',
                            'val': {
                                'name': 'id',
                                'op': 'eq',
                                'val': self.gameobjects[self.current_player_id].world.id
                            }
                        }]
                    },
                    {
                        'name': 'id',
                        'op': 'eq',
                        'val': self.current_player_id
                    }]
                }]
            };

            // Define and trace gameobject types to load
            self.gameobjects_missing = self.gameobject_types.length;

            // Clear out gameobjects
            self.gameobjects_temp = {};

            $.each(self.gameobject_types, function (i, gameobject_type) {
                self.doRequest("GET", "/api/gameobject_" + gameobject_type, self.onReturnGameObjects, {
                    q: JSON.stringify(query)
                });
            });
        } else {
            // Invalidate game
            self.gameobjects = {};

            // Call onUpdatedGameObjects on all views
            for (view of Veripeditus.views) {
                if (view.onUpdatedGameObjects) {
                    view.onUpdatedGameObjects();
                }
            }
        }
    };

    self.updateSelf = function () {
        // Request own player item
        self.doRequest("GET", "/api/gameobject_player/self", function (data) {
            self.current_player_id = data.id;
            self.gameobjects[data.id] = data;
            self.updateGameObjects();
        });
    };

    // Public method to update view boundaries, e.g. from map view
    self.setBounds = function(southWest, northEast) {
        self.bounds[0] = southWest;
        self.bounds[1] = northEast;

        self.updateGameObjects();
    };

    self.login = function(username, password) {
        localStorage.setItem("username", username);
        localStorage.setItem("password", password);

        // Update own player state
        self.updateSelf();
    };

    self.logout = function() {
        localStorage.removeItem("username");
        localStorage.removeItem("password");

        // This wil invalidate the game
        self.current_player_id = -1;
        self.updateGameObjects();
    };

    self.item_collect = function(id, view) {
        self.doRequest("GET", "/api/gameobject/" + id + "/collect", function (data) {
            view.onGameObjectActionDone(data);
            self.updateGameObjects();
        });
    };
};

GameData = new GameDataService();

// Do re-login for self-update
if (localStorage.username) {
    GameData.updateSelf();
}

Veripeditus.registerView(GameData);
