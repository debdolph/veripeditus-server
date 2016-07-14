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

var veripeditusMain = angular.module('Veripeditus', [
    'ngRoute',
    'ngResource',
    'Veripeditus.view_login',
    'Veripeditus.view_map',
]);

veripeditusMain.factory("Player", function($resource) {
    return $resource("/api/player/:id", {}, {
        query: {
                method: 'GET',
                transformResponse: function (data){
                    return angular.fromJson(data).objects;
                },
                isArray: true
               }
    });
});

veripeditusMain.factory('APIService', function($http) {
  return {
    login: function(username, password) {
      // Encode HTTP basic auth string
      // FIXME Do we need compatibility with old/broken browsers?
      var auth_string = "Basic " + window.btoa(username + ":" + password);

      // Reconfigure HTTP service
      $http.defaults.headers.common['Authorization'] = auth_string;
    }
  };
});

veripeditusMain.controller('veripeditusController', ['$scope', '$http', function ($scope, $http) {
}]);
