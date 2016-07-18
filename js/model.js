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

var default_update = {
    'update': {
        method: 'PUT'
    }
};

app.factory("Player", function($resource) {
    return $resource("/api/player/:id", {
        id: '@id'
    },
    default_update);
});

app.factory('APIModelInterceptor', function($q) {
    return {
        response: function(response) {
            try {
                // If response is a JSON object with an objects entry, extract the objects entry
                if ('objects' in response.data) {
                    response.data = angular.fromJson(response.data).objects;
                }
            } catch(err) {}

            // Return (possibly modified) response
            return response;
        }
    };
});

// FIXME Ensure that this is the last interceptor to be called!
app.config(function($httpProvider) {
    // Add a global interceptor to unwrap JSON data on query
    $httpProvider.interceptors.push('APIModelInterceptor');
});
