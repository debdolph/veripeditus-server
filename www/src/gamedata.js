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
    // Status objects
    this.bounds = [
        [0.0, 0.0],
        [0.0, 0.0]];

    // Storage objects
    this.gameobjects = {};

    // Current player object
    // FIXME get logged-in player from API
    this.current_player_id = 1;
    this.gameobjects[1] = new GameObject(1);
    this.gameobjects[1].world = {
        "id": 1
    };

    this.onGeolocationChanged = function() {
        // Update own location on server if logged in
        if (this.current_player_id > -1) {
            // Update location in player object
            this.gameobjects[this.current_player_id].latitude = Device.position.coords.latitude;
            this.gameobjects[this.current_player_id].longitude = Device.position.coords.longitude;

            // Send the PATCH request
            $.ajax({
                dataType: "json",
                contentType: "application/json",
                url: "/api/gameobject/" + this.current_player_id,
                data: JSON.stringify(this.gameobjects[this.current_player_id]),
                method: "PATCH",
                username: localStorage.getItem("username"),
                password: localStorage.getitem("password"),
            });
        }
    };

    this.onReturnGameObjects = function(data) {
        // Iterate over data and merge into gameobjects store
        for (var i = 0; i < data.objects.length; i++) {
            var go = new GameObject(data.objects[i].id);
            go.latitude = data.objects[i].latitude;
            go.longitude = data.objects[i].longitude;
            go.image = data.objects[i].image;
            go.name = data.objects[i].name;
            this.gd.gameobjects[go.id] = go;
        }

        // Call onUpdatedGameObjects on all views
        for (view of Veripeditus.views) {
            if (view.onUpdatedGameObjects) {
                view.onUpdatedGameObjects();
            }
        }
    };

    this.updateGameObjects = function() {
        // Construct JSON query filter for REST API
        var query = {
            'filters': [{
                'or': [{
                    'and': [{
                        'name': 'latitude',
                        'op': 'ge',
                        'val': this.bounds[0][0]
                    },
                    {
                        'name': 'latitude',
                        'op': 'le',
                        'val': this.bounds[1][0]
                    },
                    {
                        'name': 'longitude',
                        'op': 'ge',
                        'val': this.bounds[0][1]
                    },
                    {
                        'name': 'longitude',
                        'op': 'le',
                        'val': this.bounds[1][1]
                    },
                    {
                        'name': 'world',
                        'op': 'has',
                        'val': {
                            'name': 'id',
                            'op': 'eq',
                            'val': this.gameobjects[this.current_player_id].world.id
                        }
                    }]
                },
                {
                    'name': 'id',
                    'op': 'eq',
                    'val': this.current_player_id
                }]
            }]
        };

        $.ajax({
            dataType: "json",
            contentType: "applicaiton/json",
            url: "/api/gameobject",
            data: {
                q: JSON.stringify(query),
            },
            username: localStorage.getItem("username"),
            password: localStorage.getItem("password"),
            gd: this,
            success: this.onReturnGameObjects
        });
    };

    // Public method to update view boundaries, e.g. from map view
    this.setBounds = function(southWest, northEast) {
        this.bounds[0] = southWest;
        this.bounds[1] = northEast;

        this.updateGameObjects();
    };

    this.login = function(username, password) {
        localStorage.setItem("username", username);
        localStorage.setItem("password", password);
        // FIXME Update game state here
    };

    this.logout = function() {
        localStorage.removeItem("username");
        localStorage.removeItem("password");
        // FIXME Update game state here
    };
};

GameData = new GameDataService();
Veripeditus.registerView(GameData);
