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
    this.locationOptions = {
        enableHighAccuracy: true,
        maximumAge: 0
    };

    // Stores the id of the watchPosition() service
    this.watchId = -1;
    // Stores the last position from the Geolocation service
    this.position = {
        coords: {
            latitude: 0.0,
            longitude: 0.0,
            accuracy: 0
        },
        timestamp: 0
    };

    // Callback for Geolocation's watchPosition()
    this.onLocationUpdate = function(newpos) {
        // Store coords and timestamp from Geolocation service
        this.position.coords = newpos.coords;
        this.position.timestamp = newpos.timestamp;

        // Call onGeolocationChanged on all views
        $.each(Veripeditus.views, function(id, view) {
            if (view.onGeolocationChanged) {
                view.onGeolocationChanged();
            }
        });
    };

    // Callback for Geolocation errors
    this.onLocationError = function(error) {
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
    this.startLocation = function() {
        // Store watchId for later clearing
        this.watchId = window.navigator.geolocation.watchPosition(function(newpos) {
            self.onLocationUpdate.call(self, newpos);
        },
        this.onLocationError, this.locationOptions);
    }

    // Stop watching Geolocation
    this.stopLocation = function() {
        // Only clear if a watch is actually active
        if (this.watchId) {
            // Clear previously stored watchId
            window.navigator.geolocation.clearWatch(this.watchId);
            this.watchId = undefined;
        }
    }

    // Video constraints
    this.mediaConstraints = {
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
    this.cameraUrl = undefined;
    this.cameraStream = undefined;

    // Start camera by getting user media
    this.startCamera = function() {
        // Look for running stream
        if (!this.cameraStream) {
            navigator.mediaDevices.getUserMedia(this.mediaConstraints).then(function(stream) {
                this.cameraStream = stream;
                this.cameraUrl = window.URL.createObjectURL(stream);

                // Call onCameraChanged on all views
                $.each(Veripeditus.views, function(id, view) {
                    if (view.onCameraChanged) {
                        view.onCameraChanged();
                    }
                });
            });
        }
    };

    // Stop camera
    this.stopCamera = function() {
        if (this.cameraStream) {
            this.cameraStream.getTracks()[0].stop();
            this.cameraStream = undefined;

            // Call onCameraChanged on all views
            $.each(Veripeditus.views, function(id, view) {
                if (view.onCameraChanged) {
                    view.onCameraChanged();
                }
            });
        }
    }

    // Fullscreen state
    this.fullscreen = {
        enabled: false
    };

    // Subscribe to fullscreen change event
    document.onmozfullscreenchange = function() {
        if (document.mozFullScreenElement) {
            this.fullscreen.enabled = true;
        } else {
            this.fullscreen.enabled = false;
        }
    };

    // Start fullscreen mode
    this.startFullscreen = function() {
        if (document.body.requestFullScreen) {
            document.body.requestFullScreen();
        } else if (document.body.mozRequestFullScreen) {
            document.body.mozRequestFullScreen();
        } else if (document.body.webkitRequestFullScreen) {
            document.body.webkitRequestFullScreen();
        }
    };

    // Stop fullscreen mode
    this.stopFullscreen = function() {
        if (document.cancelFullScreen) {
            document.cancelFullScreen();
        } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        } else if (document.webkitCancelFullScreen) {
            document.webkitCancelFullScreen();
        }
    };

    // Storage for orientation data
    this.orientation = {
        absolute: false,
        alpha: 0,
        beta: 0,
        gamma: 0,
        heading: 0
    };

    // Determine browser/screen orientation
    this.browserOrientation = function() {
        if (screen.orientation && screen.orientation.type) {
            return screen.orientation.type;
        } else {
            return screen.orientation || screen.mozOrientation || screen.msOrientation;
        }
    };

    // Event handler for device oreintation changes
    this.handleOrientation = function(event) {
        // Store values
        this.orientation.absolute = event.absolute;
        this.orientation.alpha = event.alpha;
        this.orientation.beta = event.beta;
        this.orientation.gamma = event.gamma;

        // Calculate compass heading
        var heading = event.alpha;
        var orientation = this.browserOrientation();
        var adjustment = 0;
        if (this.defaultOrientation == "landscape") {
            adjustment -= 90;
        }
        if (this.defaultOrientation != orientation.split("-")[0]) {
            if (this.defaultOrientation == "landscape") {
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
        this.orientation.heading = Math.round(360 - heading);

        // Call onOrientationChanged on all views
        $.each(Veripeditus.views, function(id, view) {
            if (view.onOrientationChanged) {
                view.onOrientationChanged();
            }
        });
    };

    // Start listening for orientation events
    var handleOrientation = function(event) {
        self.handleOrientation.call(self, event);
    };
    this.startOrientation = function() {
        // Add global event handler
        window.addEventListener('deviceorientation', handleOrientation, true);
    };

    // Stop listening for orientation events
    this.stopOrientation = function() {
        // Remove global event listener
        window.removeEventListener('deviceorientation', handleOrientation, true);

        // Reset orientation data
        this.orientation = {
            absolute: false,
            alpha: 0,
            beta: 0,
            gamma: 0,
            heading: 0
        };
    };

    // Determine default orientation of device
    if (screen.width > screen.height) {
        this.defaultOrientation = "landscape";
    } else {
        this.defaultOrientation = "portrait";
    }
};

Device = new DeviceService();
Device.startOrientation();
Device.startLocation();
