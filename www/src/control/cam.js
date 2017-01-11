/*
 * veripeditus-web - Web frontend to the veripeditus server
 * Copyright (C) 2016, 2017  Dominik George <nik@naturalnet.de>
 * Copyright (C) 2017  Eike Jesinghaus <eike@naturalnet.de>
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
    var self = this;

    log_debug("Loading CamController.");

    self.MAX_DISTANCE = 100;

    // Find video view
    self.cam = $("#cam");

    // Called by DeviceService on camera stream change
    self.onCameraChanged = function() {
        log_debug("Camera stream changed. New URL: " + Device.cameraUrl);

        // Update stream URL of video view
        self.cam.attr("src", Device.cameraUrl);
        self.cam.on("loadedmetadata", function() {
            self.cam.play();
        });
    };

    this.getARStyle = function(gameobject) {
        log_debug("Assembling AR style for gameobject id " + gameobject.id + ".");

        // Target object
        var style = {}

        // Get perspective value
        // FIXME get dynamically
        var perspective = 800;

        // Center image first
        var width = $("#argameobject-" + gameobject.id).width();
        style['left'] = ((screen.width - width) / 2) + "px";

        // Get own LatLng
        var own_latlng = L.latLng(Device.position.coords.latitude, Device.position.coords.longitude);
        // Get gameobject LatLng
        var gameobject_latlng = L.latLng(gameobject.attributes.latitude, gameobject.attributes.longitude);

        // Get distance and bearing
        var distance = own_latlng.distanceTo(gameobject_latlng);
        var bearing = own_latlng.bearingTo(gameobject_latlng);
        // Determine difference of bearing and device orientation
        var bearing_diff = Device.orientation.heading - bearing;

        log_debug("Gameobject is " + distance + "m in " + bearing + "°, diff " + bearing_diff + "°.");

        if (((-bearing_diff) % 360) > 270 || ((-bearing_diff) % 360) < 90) {
            // Calculate offsets in 3D space in relation to camera
            var angle = (((-bearing_diff) % 360) / 360) * L.LatLng.DEG_TO_RAD;
            var tx = Math.sin(angle) * (perspective * (distance / self.MAX_DISTANCE));
            var ty = 0;
            var tz = perspective - Math.cos(angle) * (perspective * (distance / self.MAX_DISTANCE));

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

    // Already created images for gameobjects will be stored here.
    self.gameobject_images = {};

    // Called by GameDataService on gameobject update
    self.onUpdatedGameObjects = function() {
        log_debug("CamController received update of gameobjects.");

        // Iterate over gameobjects and add images
        $.each(GameData.gameobjects, function(id, gameobject) {
            log_debug("Inspecting gameobject id " + id + ".");

            // Check whether item should be shown
            if (!gameobject.attributes.isonmap) {
                log_debug("Item is not on map.");
                return;
            }

            // Skip if object is own player
            // FIXME isn't this replaced by isonmap with VISIBLE_SELF?
            if (id == GameData.current_player_id) {
                return;
            }

            // Look for already created image for gameobject id
            var image = self.gameobject_images[gameobject.id];
            if (! image) {
                // Image does not exist
                // Construct image element
                image = $("<img>", {
                    id: "argameobject-" + gameobject.id,
                    "class": "argameobject",
                    src: '/api/v2/gameobject/' + gameobject.id + '/image_raw'
                });

                // Add image to DOM
                $("div#arview").append(image);
                self.gameobject_images[gameobject.id] = image;

                log_debug("Created image.");
            } else {
                log_debug("Found existing image.");
            }

            // Update style of image element
            image.css(self.getARStyle(gameobject));
        });

        // Iterate over found images and remove everything not found in gameobjects
        $.each(self.gameobject_images, function(id, image) {
            log_debug("Inspecting gameobject id " + id + ".");

            if ($.inArray(id, Object.keys(GameData.gameobjects)) == -1) {
                // Remove image if object vanished from gameobjects
                image.remove();
                delete self.gameobject_images[id];
                log_debug("No longer exists, removing.");
            } else if (!GameData.gameobjects[id].attributes.isonmap) {
                // Remove image if object is not visible on map anymore
                image.remove();
                delete self.gameobject_images[id];
                log_debug("No longer on map, removing.");
            }
        });
    };

    // Called by DeviceService on geolocation change
    self.onGeolocationChanged = function() {
        log_debug("CamController received geolocation change.");

        // Calculate view bounds
        // FIXME come up with something smarter
        var bounds = [
            [Device.position.coords.latitude - 0.001, Device.position.coords.longitude - 0.001],
            [Device.position.coords.latitude + 0.001, Device.position.coords.longitude + 0.001]];

        // Update bounds in GameDataService
        GameData.setBounds(bounds[0], bounds[1]);
    };

    // Called by DeviceService on orientation change
    self.onOrientationChanged = function() {
        log_debug("CamController received orientation change.");

        // Update AR style for all objects
        $.each(self.gameobject_images, function(id, image) {
            image.css(self.getARStyle(GameData.gameobjects[id]));
        });
    };

    self.activate = function() {
        $("div#camview").show();;
        Device.startCamera();
        log_debug("CamController activated.");
    };

    self.deactivate = function() {
        $("div#camview").hide();
        Device.stopCamera();
        log_debug("CamController deactivated.");
    };
};

// Instantiate controller and register to services
CamView = new CamController();
Veripeditus.registerView(CamView);
