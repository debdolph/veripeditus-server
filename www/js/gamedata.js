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

// Service for the Player API object
app.factory("GameDataService", function($rootScope, $resource, $log, APIBasicAuth, DeviceService) {
    // Get a local scope so events propagate correctly
    var $scope = $rootScope.$new();

    // Declare a new update() method for all services, passed to $resource in factories
    var default_update = {
        'update': {
            // PATCH method allows partial updates
            method: 'PATCH'
        }
    };

    // Define $resource service to API endpoint Player
    var resPlayer = $resource("/api/player/:id", {
        id: '@id'
    },
    default_update);

    // Status objects
    var bounds = [
        [0.0, 0.0],
        [0.0, 0.0]];

    // Storage objects
    var players = {};

    // Player object
    function Player(id) {
        this.id = id;
        this.latitude = 0.0;
        this.longitude = 0.0;
    }

    // Subscribe to broadcast event from DeviceService
    $scope.$on('Geolocation.changed', function(event, position) {
        // Update own location on server if logged in
        if (APIBasicAuth.loggedin()) {
            res.update({
                // Player.id from user in server_info (currently logged in)
                id: APIBasicAuth.server_info.user.id
            },
            {
                // Position from DeviceService
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            });
        }
    });

    // Subscribe to (own) event upon updating view bounds
    $scope.$on('GameData.updated.bounds', function(event) {
        updatePlayers();
    });

    function updatePlayers() {
        // Construct JSON query filter for REST API
        var query = {
            'filters': [{
                'and': [{
                    'name': 'latitude',
                    'op': 'ge',
                    'val': bounds[0][0]
                },
                {
                    'name': 'latitude',
                    'op': 'le',
                    'val': bounds[1][0]
                },
                {
                    'name': 'longitude',
                    'op': 'ge',
                    'val': bounds[0][1]
                },
                {
                    'name': 'longitude',
                    'op': 'le',
                    'val': bounds[1][1]
                }]
            }]
        };

        // Send query to REST API
        $log.debug("Querying players within (" + bounds[0][0] + ", " + bounds[0][1] + ") (" + bounds[1][0] + ", " + bounds[1][1] + ")");
        resPlayer.query({
            q: query
        },
        function(data) {
            // Iterate over data and merge into players store
            for (var i = 0; i < data.length; i++) {
                // Skip own player because it is handled separately
                if (APIBasicAuth.loggedin() && data[i].id == APIBasicAuth.server_info.user.id) {
                    continue;
                }

                var player = new Player(data[i].id);
                player.latitude = data[i].latitude;
                player.longitude = data[i].longitude;
                player.avatar = data[i].avatar;
                player.username = data[i].username;
                player.name = data[i].username;
                players[player.id] = player;
            }

            // Broadcast event that position changed
            $rootScope.$broadcast('GameData.updated.players', players);
        });
    }

    // Public method to update view boundaries, e.g. from map view
    function setBounds(southWest, northEast) {
        bounds[0] = southWest;
        bounds[1] = northEast;

        // Tell everyone we updated the view bounds
        $rootScope.$broadcast('GameData.updated.bounds', bounds);
    }

    // Publish
    return {
        players: players,
        setBounds: setBounds
    };
});

// Interceptor to transform API requests and responses
app.factory('APIModelInterceptor', function() {
    return {
        response: function(response) {
            // If response is a JSON object with an objects entry, extract the objects entry
            if (typeof response.data === "object" && 'objects' in response.data) {
                response.data = angular.fromJson(response.data).objects;
            }

            // Return (possibly modified) response
            return response;
        }
    };
});

// Configure HTTP provider
app.config(function($httpProvider) {
    // Add a global interceptor for ngFancyREST
    $httpProvider.interceptors.push('APIInterceptor');
    // Add a global interceptor to unwrap JSON data on query
    $httpProvider.interceptors.push('APIModelInterceptor');
    // Add a global interceptor that watches for a 401 status
    // and redirects to /login if necessary
    $httpProvider.interceptors.push('APILoginInterceptor');
});
