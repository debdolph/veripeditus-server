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

var VERSION = "0.1";

var veripeditusMain = angular.module('Veripeditus', [
    'ngRoute',
    'ngResource',
    'Veripeditus.view_login',
    'Veripeditus.view_logout',
    'Veripeditus.view_map',
    'Veripeditus.view_register',
]);

veripeditusMain.factory("Player", function($resource) {
    return $resource("/api/player/:id");
});

veripeditusMain.factory('APIService', function($http, Messages) {
  return {
    login: function(username, password, remember) {
      // Encode HTTP basic auth string
      // FIXME Do we need compatibility with old/broken browsers?
      var auth_string = "Basic " + window.btoa(username + ":" + password);

      // Reconfigure HTTP service
      $http.defaults.headers.common['Authorization'] = auth_string;

      // Store auth string in session storage
      sessionStorage.auth_string = auth_string;
      // Also store in local persistent storage if desired
      if (remember) {
        localStorage.auth_string = auth_string;
      }
    },
    logout: function() {
      // Reconfigure HTTP service
      $http.defaults.headers.common['Authorization'] = "";

      // Add floating message
      Messages.add('info', 'You have been logged out.');

      // Remove auth string from all storages
      delete sessionStorage['auth_string'];
      delete localStorage['auth_string'];
    }
  };
});

// Service for floating messages
veripeditusMain.factory('Messages', function($rootScope, $timeout) {
  function remove(id) {
    // Clear the timer first
    $timeout.cancel($rootScope.msgs[id].tid);
    delete $rootScope.msgs[id];
  }

  return {
    add: function(cls, message) {
      var id = Math.max.apply(null, Object.keys($rootScope.msgs)) + 1;
      $rootScope.msgs[id] = {'class': cls, 'message': message};

      // Add timer to auto-close the message
      var tid = $timeout(remove, 10000, true, id);
      $rootScope.msgs[id].tid = tid;
    },
    'remove': remove
  };
});

// FIXME This sure needs to be overhauled.
veripeditusMain.factory('APILoginInterceptor', function($location, $rootScope) {
  return {
    response: function(response) {
      try {
        // Copy server info if it is inside the response
        // Doing this for every response that has it for live migrations on server-side
        $rootScope.server_info = angular.copy(angular.fromJson(response.data).server_info);
      } catch(err) {
      }

      try {
        // If response is a JSON object with an objects entry, extract the objects entry
        response.data = angular.fromJson(response.data).objects;
      } catch(err) {
      }

      // Return (possibly modified) response
      return response;
    },
    responseError: function(response) {
      if (response.status == 401) {
        $location.url("/login");
      }
      return response;
    }
  };
});

veripeditusMain.config(['$httpProvider', function($httpProvider) {
  // Add a global interceptor that watches for a 401 status
  // and redirects to /login if necessary
  $httpProvider.interceptors.push('APILoginInterceptor');
}]);

veripeditusMain.controller('veripeditusController', ['$scope', '$rootScope', '$location', '$http', 'Messages', function ($scope, $rootScope, $location, $http, Messages) {
  $rootScope.VERSION = VERSION;

  // Object to hold all the floating messages
  // contains a set of id: {class: 'alert class', message: 'foo'} objects
  $rootScope.msgs = {}

  // Bind $rootScope into controller scope to make it available
  // in data bindings
  $scope.root = $rootScope;

  // Function that passes closing of a floating alert to the Messages service
  $scope.closeAlert = function(id) {
    Messages.remove(id);
  };

  // Look for auth string in session storage, then local storage
  var s_auth_string = sessionStorage.auth_string || localStorage.auth_string;
  // Set to HTTP service if auth string was stored
  if (s_auth_string) {
    $http.defaults.headers.common['Authorization'] = s_auth_string;
  }

  // Default to /map for now
  $location.url("/map");
}]);

$(function () {
	// Used to automatically restyle content area when window size changes,
	// because that might resize the header and footer areas as well
	var resizeFunction = function () {
		var header = document.getElementById("navbar-header").offsetHeight;
		var footer = document.getElementById("footer").offsetHeight;

		// Hide footer if display is too small
		if ($(window).height() < header * 6) {
			$("#footer").hide();
			footer = 0;
		} else {
			$("#footer").show();
		}

		$("#content-outer").css("top", header).height($(window).height() - header - footer);
	    };
	resizeFunction();
	$(window).on('resize', resizeFunction);

	// Collapse navbar on menu click
	$('.nav a').click(function () {
	    $('.navbar-collapse').collapse('hide');
	});
    });
