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

app.controller('ViewCamController', function($log, $document, $scope, GameDataService, DeviceService) {
    const MAX_DISTANCE = 100;

    // Find video view
    $scope.cam = $document.find('video')[0];

    // Subscribe to update event from DeviceService
    $scope.$on('Camera.changed', function(event, url) {
        // Update stream URL of video view
        $scope.cam.src = url;
        $scope.cam.onloadedmetadata = function() {
            $scope.cam.play();
        };
    });

    // Stop camera upon leaving this view
    // FIXME move to state controller, probably
    $scope.$on('$destroy', function() {
        DeviceService.stopCamera();
    });

    // Start camera
    DeviceService.startCamera();

    // Utility functions for generating player images
    $scope.getARStyle = function(player) {
        // Target object
        var style = {}

        // Get perspective value
        // FIXME get dynamically
        var perspective = 800;

        // Center image first
        var width = document.getElementById("arplayer-" + player.id).width;
        style.left = ((screen.width - width) / 2) + "px";

        // Get own LatLng
        var own_latlng = L.latLng(DeviceService.position.coords.latitude, DeviceService.position.coords.longitude);
        // Get player LatLng
        var player_latlng = L.latLng(player.latitude, player.longitude);

        // Get distance and bearing
        var distance = own_latlng.distanceTo(player_latlng);
        var bearing = own_latlng.bearingTo(player_latlng);
        // Determine difference of bearing and device orientation
        var bearing_diff = DeviceService.orientation.alpha - bearing;

        // Calculate offsets in 3D space in relation to camera
        var angle = (((-bearing_diff) % 360) / 360) * (2 * Math.PI);
        var tx = Math.sin(angle) * perspective;
        var ty = 0;
        var tz = perspective - Math.cos(angle) * (perspective * (distance / 100));

        // Generate transform functions
        var rotation = "rotateY(" + (bearing_diff) + "deg)";
        var offset = "translate3d(" + tx + "px, " + ty + "px, " + tz + "px)";

        // Generate CSS transform attribute
        style.transform = rotation + " " + offset;

        return style;
    };
    $scope.getPlayerAvatar = function(player) {
        return '/api/data/avatar_' + player.avatar + '.svg';
    };

    // Subscribe to data updates for surrounding players
    $scope.$on('GameData.updated.players', function(event, players) {
        // Map players into scope
        $scope.players = angular.copy(players);
    });

    // Subcribe to geolocation updates
    $scope.$on('Geolocation.changed', function(event, position) {
        // Calculate view bounds
        // FIXME come up with something smarter
        var bounds = [
            [position.coords.latitude - 0.001, position.coords.longitude - 0.001],
            [position.coords.latitude + 0.001, position.coords.longitude + 0.001]];

        // Update bounds in GameDataService
        GameDataService.setBounds(bounds[0], bounds[1]);
    });

    // Subcribe to orientation updates
    $scope.$on('Orientation.changed', function(event) {
        // Force update of player images
        // FIXME come up with something better
        $scope.players = angular.copy($scope.players);
    });
});
