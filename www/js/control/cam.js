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
});
