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

/** global: L */

app.controller('ViewMapController', function($log, $scope, Player, LocationService) {
    // Set up map view
    $scope.map = L.map("map");
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo($scope.map);

    // Add initial marker for own position
    $scope.marker_self = L.marker([LocationService.position.coords.latitude, LocationService.position.coords.longitude]);
    $scope.marker_self.addTo($scope.map);
    $scope.circle_self = L.circle($scope.marker_self.getLatLng(), 0);
    $scope.circle_self.addTo($scope.map);

    // Initially center map view to own position
    $scope.map.setView($scope.marker_self.getLatLng(), 16);

    // Already created markers for players will be stored here.
    $scope.player_markers = {};

    // Function that loads all players in the visible map area, to be used as
    function getPlayersOnMap() {
        // Get bounds of map
        var bounds = $scope.map.getBounds();
        // Construct JSON query filter for REST API
        var query = {
            'filters': [{
                'and': [{
                    'name': 'latitude',
                    'op': 'ge',
                    'val': bounds.getSouth()
                },
                {
                    'name': 'latitude',
                    'op': 'le',
                    'val': bounds.getNorth()
                },
                {
                    'name': 'longitude',
                    'op': 'ge',
                    'val': bounds.getWest()
                },
                {
                    'name': 'longitude',
                    'op': 'le',
                    'val': bounds.getEast()
                }]
            }]
        };

        // Send query to REST API
        $log.debug("Querying players within (" + bounds.getSouth() + ", " + bounds.getWest() + ") (" + bounds.getNorth() + ", " + bounds.getEast() + ")");
        Player.query({
            q: query
        },
        function(data) {
            // Store entire response
            $scope.players = data;

            // Iterate over players and add map markers
            for (var i = 0; i < $scope.players.length; i++) {
                var player = $scope.players[i];

                // Look for already created marker for this player id
                var marker = $scope.player_markers[player.id];
                if (marker) {
                    // Marker exists, store location
                    marker.setLatLng([player.latitude, player.longitude]);
                    $log.debug("Map: Reusing marker for player id " + player.id);
                } else {
                    // Marker does not exist
                    $log.debug("Map: Creating new marker for player id " + player.id);

                    // Construct marker icon from base64 encoded player avatar
                    var picon = L.icon({
                        'iconUrl': 'data:image/png;base64,' + player.avatar_base64,
                        'iconSize': [32, 32],
                    });

                    // Create marker at player location
                    marker = L.marker([player.latitude, player.longitude], {
                        'icon': picon
                    });

                    // Create simple popup with basic information
                    marker.bindPopup("<p>Username: " + player.username + "<br />Name: " + player.name + "</p>");

                    // Add marker to map and store to known markers
                    marker.addTo($scope.map);
                    $scope.player_markers[player.id] = marker;
                }
            }
        });
    }

    // Subscribe to broadcast event from LocationService
    $scope.$on('Geolocation.changed', function(event, position) {
        // Update position of own marker
        $scope.marker_self.setLatLng([position.coords.latitude, position.coords.longitude]);

        // Update accuracy radius around own marker
        $scope.circle_self.setLatLng($scope.marker_self.getLatLng());
        $scope.circle_self.setRadius(position.coords.accuracy);

        // Center map at own marker
        $scope.map.setView($scope.marker_self.getLatLng());
    });

    // Subscribe to event on change of map view
    $scope.map.on('moveend', function() {
        // Update players on new map view
        getPlayersOnMap();
    });

    // Initially get players
    getPlayersOnMap();
});
