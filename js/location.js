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

app.factory('LocationService', function($rootScope, $log, $window, Messages) {
    // Options to give to the Geolocation API
    var locationOptions = {
        enableHighAccuracy: true,
        maximumAge: 0
    };

    var watchId;
    var position = {
        coords: {
            latitude: 0.0,
            longitude: 0.0
        }
    };

    // Callback for Geolocation's watchPosition()
    function onLocationUpdate(newpos) {
        $rootScope.$apply(function() {
            position.coords = newpos.coords;
            position.timestamp = newpos.timestamp;
            $rootScope.$broadcast('Geolocation.changed', position);
        });
    }

    // Callback for Geolocation errors
    function onLocationError(error) {
        var msg;
        if (error.code == error.PERMISSION_DENIED) {
            msg = "Permission for tracking location denied.";
        } else if (error.code == error.POSITION_UNAVAILABLE) {
            msg = "Position unavailable.";
        } else if (error.code == error.TIMEOUT) {
            msg = "Timeout acquiring location.";
        } else {
            msg = "Unknown error acquiring location.";
        }
        Messages.add("danger", msg);
    }

    // Start watching Geolocation
    function start() {
        this.watchId = $window.navigator.geolocation.watchPosition(onLocationUpdate, onLocationError, locationOptions);
    }

    // Stop watching Geolocation
    function stop() {
        if (this.watchId) {
            $window.navigator.geolocation.clearWatch(this.watchId);
            this.watchId = undefined;
        }
    }

    return {
        start: start,
        stop: stop,
        position: position
    };
});
