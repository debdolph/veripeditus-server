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

// Declare a new update() method for all services, passed to $resource in factories
var default_update = {
    'update': {
        // PATCH method allows partial updates
        method: 'PATCH'
    }
};

// Service for the Player API object
app.factory("Player", function($rootScope, $resource, APIBasicAuth) {
    // Define $resource service to API endpoint
    var res = $resource("/api/player/:id", {
        id: '@id'
    },
    default_update);

    // Subscribe to broadcast event from LocationService
    $rootScope.$on('Geolocation.changed', function(event, position) {
        // Update own location on server if logged in
        if (APIBasicAuth.loggedin()) {
            res.update({
                // Player.id from user in server_info (currently logged in)
                id: APIBasicAuth.server_info.user.id
            },
            {
                // Position from LocationService
                latitude: position.coords.latitude,
                longitude: position.coords.longitude
            });
        }
    });

    // Publish $resource service
    return res;
});

// Interceptor to transform API requests and responses
app.factory('APIModelInterceptor', function() {
    return {
        response: function(response) {
            // If response is a JSON object with an objects entry, extract the objects entry
            if (typeof response.data === "object" && 'objects' in response.data) {
                response.data = angular.fromJson(response.data).objects;
            }

            // Return (possibly modified) response
            return response;
        }
    };
});

// Configure HTTP provider
app.config(function($httpProvider) {
    // Add a global interceptor to unwrap JSON data on query
    $httpProvider.interceptors.push('APIModelInterceptor');
    // Add a global interceptor that watches for a 401 status
    // and redirects to /login if necessary
    $httpProvider.interceptors.push('APILoginInterceptor');
});
