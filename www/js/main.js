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

var VERSION = "0.1";

// Main application module
var app = angular.module('Veripeditus', ['ngRoute', 'ngResource', 'gettext', 'ui.bootstrap', 'ngFancyREST', 'ngBasicAuth', 'ngFloatingMessages']);

// One-time setup code for entire application
app.run(function($rootScope, $location, $uibModal, APIService, APIBasicAuth, DeviceService, Messages) {
    // Publish some constants and services to all scopes
    $rootScope.VERSION = VERSION;
    $rootScope.$location = $location;
    $rootScope.APIBasicAuth = APIBasicAuth;
    $rootScope.APIService = APIService;
    $rootScope.Messages = Messages;
    $rootScope.DeviceService = DeviceService;

    // FIXME move to some better place
    $rootScope.loginDialog = function() {
        var mi = $uibModal.open({
            templateUrl: 'html/login.html',
            controller: 'ViewLoginController'
        });
        // FIXME check promise; e.g. react to login by loading something
    };

    // Start location service so all controllers receive location updates
    DeviceService.startLocation();
});
