/*
 * veripeditus-web - Web frontend to the veripeditus server
 * Copyright (C) 2016  Dominik George <nik@naturalnet.de>
 * Copyright (c) 2016  mirabilos <m@mirbsd.org>
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
    'Veripeditus.view_register',
]);

veripeditusMain.factory("Player", function($resource, $location, $rootScope) {
    return $resource("/api/player/:id", {}, {
        query: {
                method: 'GET',
                transformResponse: function (data){
                    $rootScope.server_info = angular.copy(angular.fromJson(data).server_info);
                    return angular.fromJson(data).objects;
                },
                isArray: true
               },
        get: {
              method: 'GET',
              transformResponse: function (data){
                  $rootScope.server_info = angular.copy(angular.fromJson(data).server_info);
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

// FIXME This sure needs to be overhauled.
veripeditusMain.factory('APILoginInterceptor', function($location) {
  return {
    responseError: function(response) {
      if (response.status == 401) {
        $location.url("/login");
      }
      return false;
    }
  };
});

veripeditusMain.config(['$httpProvider', function($httpProvider) {
  $httpProvider.interceptors.push('APILoginInterceptor');
}]);

veripeditusMain.controller('veripeditusController', ['$scope', '$rootScope', function ($scope, $rootScope) {
  $scope.root = $rootScope;
}]);

$(function () {
	var resizeFunction = function () {
		var header = document.getElementById("navbar-header").offsetHeight;
		var footer = document.getElementById("footer").offsetHeight;
		$("#css-sucks-wrapper").css("top", header).height($(window).height() - header - footer);
	    };
	resizeFunction();
	$(window).on('resize', resizeFunction);
    });
