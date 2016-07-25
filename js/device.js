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

app.factory('DeviceService', function($rootScope, $log, $window, Messages) {
    // Options to give to the Geolocation API
    var locationOptions = {
        enableHighAccuracy: true,
        maximumAge: 0
    };

    // Stores the id of the watchPosition() service
    var watchId;
    // Stores the last position from the Geolocation service
    var position = {
        coords: {
            latitude: 0.0,
            longitude: 0.0,
            accuracy: 0
        },
        timestamp: 0
    };

    // Callback for Geolocation's watchPosition()
    function onLocationUpdate(newpos) {
        // Get this function back into scope after being called from navigator
        $rootScope.$apply(function() {
            // Store coords and timestamp from Geolocation service
            position.coords = newpos.coords;
            position.timestamp = newpos.timestamp;

            // Broadcast event that position changed
            $rootScope.$broadcast('Geolocation.changed', position);
        });
    }

    // Callback for Geolocation errors
    function onLocationError(error) {
        // Stores message after finding out what caused the error
        var msg;

        // Check error code and select own message
        if (error.code == error.PERMISSION_DENIED) {
            msg = "Permission for tracking location denied.";
        } else if (error.code == error.POSITION_UNAVAILABLE) {
            msg = "Position unavailable.";
        } else if (error.code == error.TIMEOUT) {
            msg = "Timeout acquiring location.";
        } else {
            msg = "Unknown error acquiring location.";
        }

        // Add floating message
        Messages.add("danger", msg);
    }

    // Start watching Geolocation
    function startLocation() {
        // Store watchId for later clearing
        this.watchId = $window.navigator.geolocation.watchPosition(onLocationUpdate, onLocationError, locationOptions);
    }

    // Stop watching Geolocation
    function stopLocation() {
        // Only clear if a watch is actually active
        if (this.watchId) {
            // Clear previously stored watchId
            $window.navigator.geolocation.clearWatch(this.watchId);
            this.watchId = undefined;
        }
    }

    // Video constraints
    var mediaConstraints = {
        audio: false,
        video: {
            width: $window.innerWidth,
            height: $window.innerHeight,
            facingMode: {
                exact: "environment"
            }
        }
    };

    // Stores the stream URL for the camera and internal stream object
    var cameraUrl;
    var cameraStream;

    // Start camera by getting user media
    function startCamera() {
        // Look for running stream
        if (!cameraStream) {
            navigator.mediaDevices.getUserMedia(mediaConstraints).then(function(stream) {
                cameraStream = stream;
                cameraUrl = $window.URL.createObjectURL(stream);
                $rootScope.$broadcast("Camera.changed", cameraUrl);
            }).catch(function(error) {
                Messages.add("danger", error.message);
            });
        }
    }

    // Stop camera
    function stopCamera() {
        if (cameraStream) {
            cameraStream.getTracks()[0].stop();
            cameraStream = undefined;

            // Tell others the stream was stopped
            $rootScope.$broadcast('Camera.stopped');
        }
    }

    // Publish service API
    return {
        startLocation: startLocation,
        stopLocation: stopLocation,
        startCamera: startCamera,
        stopCamera: stopCamera,
        position: position,
        cameraUrl: cameraUrl
    };
});
