/*
 * veripeditus-web - Web frontend to the veripeditus server
 * Copyright (C) 2016  Dominik George <nik@naturalnet.de>
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

CamController = function() {
    this.MAX_DISTANCE = 100;

    // Find video view
    this.cam = $("#cam");

    // Called by DeviceService on camera stream change
    this.onCameraChanged = function() {
        // Update stream URL of video view
        this.cam.src = Device.cameraUrl;
        this.cam.onloadedmetadata = function() {
            this.cam.play();
        };
    };

    // Start camera
    Device.startCamera();
    // FIXME Stop on leave
    // Utility functions for generating gameobject images
    this.getARStyle = function(gameobject) {
        // Target object
        var style = {}

        // Get perspective value
        // FIXME get dynamically
        var perspective = 800;

        // Center image first
        var width = $("#argameobject-" + gameobject.id).width;
        style['left'] = ((screen.width - width) / 2) + "px";

        // Get own LatLng
        var own_latlng = L.latLng(Device.position.coords.latitude, Device.position.coords.longitude);
        // Get gameobject LatLng
        var gameobject_latlng = L.latLng(gameobject.latitude, gameobject.longitude);

        // Get distance and bearing
        var distance = own_latlng.distanceTo(gameobject_latlng);
        var bearing = own_latlng.bearingTo(gameobject_latlng);
        // Determine difference of bearing and device orientation
        var bearing_diff = Device.orientation.alpha - bearing;

        if (((-bearing_diff) % 360) > 270 || ((-bearing_diff) % 360) < 90) {
            // Calculate offsets in 3D space in relation to camera
            var angle = (((-bearing_diff) % 360) / 360) * L.LatLng.DEG_TO_RAD;
            var tx = Math.sin(angle) * (perspective * (distance / MAX_DISTANCE));
            var ty = 0;
            var tz = perspective - Math.cos(angle) * (perspective * (distance / MAX_DISTANCE));

            // Generate transform functions
            var rotation = "rotateY(" + (bearing_diff) + "deg)";
            var offset = "translate3d(" + tx + "px, " + ty + "px, " + tz + "px)";

            // Generate CSS transform attributes
            style['transform'] = rotation + " " + offset;
            style['-webkit-transform'] = rotation + " " + offset;
        } else {
            // Object is behind us and not visible
            style['display'] = 'none';
        }

        return style;
    };

    // Called by GameDataService on gameobject update
    this.onUpdatedGameObjects = function() {
        // FIXME do something
    };

    // Called by DeviceService on geolocation change
    this.onGeolocationChanged = function() {
        // Calculate view bounds
        // FIXME come up with something smarter
        var bounds = [
            [Device.position.coords.latitude - 0.001, Device.position.coords.longitude - 0.001],
            [Device.position.coords.latitude + 0.001, Device.position.coords.longitude + 0.001]];

        // Update bounds in GameDataService
        GameData.setBounds(bounds[0], bounds[1]);
    };

    // Called by DeviceService on orientation change
    this.onOrientationChanged = function() {
        // FIXME do something
        $('#foo').val(Device.orientation.alpha + " " + Device.orientation.beta + " " + Device.orientation.gamma);
    };
};

// Instantiate controller and register to services
CamView = new CamController();
Veripeditus.registerView(CamView);
