/*
 * veripeditus-web - Web frontend to the veripeditus server
 * Copyright (C) 2016, 2017  Dominik George <nik@naturalnet.de>
 * Copyright (C) 2016, 2017  Eike Tim Jesinghaus <eike@naturalnet.de>
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

DeviceService = function() {
    var self = this;

    // Options to give to the Geolocation API
    self.locationOptions = {
        enableHighAccuracy: true,
        maximumAge: 0
    };

    // Stores the id of the watchPosition() service
    self.watchId = -1;
    // Stores the last position from the Geolocation service
    self.position = {
        coords: {
            latitude: 0.0,
            longitude: 0.0,
            accuracy: 0
        },
        timestamp: 0
    };

    // Callback for Geolocation's watchPosition()
    self.onLocationUpdate = function(newpos) {
        // Store coords and timestamp from Geolocation service
        self.position.coords = newpos.coords;
        self.position.timestamp = newpos.timestamp;

        // Call onGeolocationChanged on all services
        $.each(Veripeditus.services, function(id, service) {
            if (service.onGeolocationChanged) {
                service.onGeolocationChanged();
            }
        });
    };

    // Callback for Geolocation errors
    self.onLocationError = function(error) {
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
    };

    // Start watching Geolocation
    self.startLocation = function() {
        // Store watchId for later clearing
        self.watchId = window.navigator.geolocation.watchPosition(function(newpos) {
            self.onLocationUpdate.call(self, newpos);
        },
        self.onLocationError, self.locationOptions);
    }

    // Stop watching Geolocation
    self.stopLocation = function() {
        // Only clear if a watch is actually active
        if (self.watchId) {
            // Clear previously stored watchId
            window.navigator.geolocation.clearWatch(self.watchId);
            self.watchId = undefined;
        }
    }

    // Video constraints
    self.mediaConstraints = {
        audio: false,
        video: {
            width: window.innerWidth,
            height: window.innerHeight,
            facingMode: {
                exact: "environment"
            }
        }
    };

    // Stores the stream URL for the camera and internal stream object
    self.cameraUrl = undefined;
    self.cameraStream = undefined;

    // Start camera by getting user media
    self.startCamera = function() {
        // Look for running stream
        if (!self.cameraStream) {
            navigator.mediaDevices.getUserMedia(self.mediaConstraints).then(function(stream) {
                self.cameraStream = stream;
                self.cameraUrl = window.URL.createObjectURL(stream);

                // Call onCameraChanged on all services
                $.each(Veripeditus.services, function(id, service) {
                    if (service.onCameraChanged) {
                        service.onCameraChanged();
                    }
                });
            });
        }
    };

    // Stop camera
    self.stopCamera = function() {
        if (self.cameraStream) {
            self.cameraStream.getTracks()[0].stop();
            self.cameraStream = undefined;

            // Call onCameraChanged on all services
            $.each(Veripeditus.services, function(id, service) {
                if (service.onCameraChanged) {
                    service.onCameraChanged();
                }
            });
        }
    }

    // Fullscreen state
    self.fullscreen = {
        enabled: false
    };

    // Subscribe to fullscreen change event
    document.onmozfullscreenchange = function() {
        if (document.mozFullScreenElement) {
            self.fullscreen.enabled = true;
        } else {
            self.fullscreen.enabled = false;
        }
    };

    // Start fullscreen mode
    self.startFullscreen = function() {
        if (document.body.requestFullScreen) {
            document.body.requestFullScreen();
        } else if (document.body.mozRequestFullScreen) {
            document.body.mozRequestFullScreen();
        } else if (document.body.webkitRequestFullScreen) {
            document.body.webkitRequestFullScreen();
        }
    };

    // Stop fullscreen mode
    self.stopFullscreen = function() {
        if (document.cancelFullScreen) {
            document.cancelFullScreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.webkitCancelFullScreen) {
            document.webkitCancelFullScreen();
        }
    };

    // Storage for orientation data
    self.orientation = {
        absolute: false,
        alpha: 0,
        beta: 0,
        gamma: 0,
        heading: 0
    };

    // Determine browser/screen orientation
    self.browserOrientation = function() {
        if (screen.orientation && screen.orientation.type) {
            return screen.orientation.type;
        } else {
            return screen.orientation || screen.mozOrientation || screen.msOrientation;
        }
    };

    // Event handler for device oreintation changes
    self.handleOrientation = function(event) {
        // Store values
        self.orientation.absolute = event.absolute;
        self.orientation.alpha = event.alpha;
        self.orientation.beta = event.beta;
        self.orientation.gamma = event.gamma;

        // Calculate compass heading
        if (event.heading) {
            self.orientation.heading = event.heading;
        } else {
            var heading = event.alpha;
            var orientation = self.browserOrientation();
            var adjustment = 0;
            if (self.defaultOrientation == "landscape") {
                adjustment -= 90;
            }
            if (self.defaultOrientation != orientation.split("-")[0]) {
                if (self.defaultOrientation == "landscape") {
                    adjustment -= 270;
                } else {
                    adjustment -= 90;
                }
            }
            if (orientation.split("-")[1] == "secondary") {
                adjustment -= 180;
            }
            heading = heading + adjustment;
            if (heading < 0) {
                heading = heading + 360;
            }
            self.orientation.heading = Math.round(360 - heading);
        }

        // Call onOrientationChanged on all services
        $.each(Veripeditus.services, function(id, service) {
            if (service.onOrientationChanged) {
                service.onOrientationChanged();
            }
        });
    };

    // Start listening for orientation events
    var handleOrientation = function(event) {
        self.handleOrientation.call(self, event);
    };
    self.startOrientation = function() {
        // Add global event handler
        window.addEventListener('deviceorientation', handleOrientation, true);
    };

    // Stop listening for orientation events
    self.stopOrientation = function() {
        // Remove global event listener
        window.removeEventListener('deviceorientation', handleOrientation, true);

        // Reset orientation data
        self.orientation = {
            absolute: false,
            alpha: 0,
            beta: 0,
            gamma: 0,
            heading: 0
        };
    };

    // Determine default orientation of device
    if (screen.width > screen.height) {
        self.defaultOrientation = "landscape";
    } else {
        self.defaultOrientation = "portrait";
    }
};

Device = new DeviceService();
Device.startOrientation();
Device.startLocation();
