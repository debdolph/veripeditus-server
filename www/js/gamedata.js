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

GameData = {
    // Status objects
    this.bounds = [
        [0.0, 0.0],
        [0.0, 0.0]];

    // Storage objects
    this.players = {};

    // Player object
    this.Player = function(id) {
        this.id = id;
        this.latitude = 0.0;
        this.longitude = 0.0;
    };

    // FIXME Subscribe to signal
    this.onGeolocationChanged = function(event, position) {
        // Update own location on server if logged in
        if (API.loggedin()) {
            // FIXME do update player location
        }
    });

    this.updatePlayers = function() {
        // Construct JSON query filter for REST API
        var query = {
            'filters': [{
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
                }]
            }]
        };

        function onReturnPlayers(data) {
            // Iterate over data and merge into players store
            for (var i = 0; i < data.length; i++) {
                // Skip own player because it is handled separately
                if (API.loggedin() && data[i].id == API.server_info.user.id) {
                    continue;
                }

                var player = new Player(data[i].id);
                player.latitude = data[i].latitude;
                player.longitude = data[i].longitude;
                player.avatar = data[i].avatar;
                player.username = data[i].username;
                player.name = data[i].username;
                this.players[player.id] = player;
            }

            // FIXME Signal new users
        });
    };
    // FIXME Send query to API

    // Public method to update view boundaries, e.g. from map view
    this.setBounds = function(southWest, northEast) {
        this.bounds[0] = southWest;
        this.bounds[1] = northEast;

        // FIXME Signal bounds update
    };
});
