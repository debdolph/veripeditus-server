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
    'gettext',
]);

var default_update = {
    'update': { method:'PUT' }
};

veripeditusMain.factory("Player", function($resource) {
    return $resource("/api/player/:id", {id: '@id'}, default_update);
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
        if ('objects' in response.data) {
          response.data = angular.fromJson(response.data).objects;
        }
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

veripeditusMain.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/login', {
    templateUrl: 'views/login.html',
    controller: 'ViewLoginController'
  });
}]).controller('ViewLoginController', ['$scope', '$window', 'APIService', function($scope, $window, APIService) {
  $scope.login = function() {
   APIService.login($scope.username, $scope.password, $scope.remember);
   // FIXME: Only on success
   $window.history.back();
  };
}]);

veripeditusMain.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/logout', {
    templateUrl: 'views/logout.html',
    controller: 'ViewLogoutController'
  });
}]).controller('ViewLogoutController', ['$scope', '$window', 'APIService', function($scope, $window, APIService) {
   APIService.logout();
   $window.history.back();
}]);

veripeditusMain.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/map', {
    templateUrl: 'views/map.html',
    controller: 'ViewMapController'
  });
}]).controller('ViewMapController', ['$scope', 'Player', function($scope, Player) {
  // Set up map view
  var map = L.map("map");
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);

  Player.query(function(data) {
    $scope.players = data;

    // FIXME: Use a more intelligent way to find map center!
    map.setView([$scope.players[0].latitude, $scope.players[0].longitude], 16);

    // Iterate over players and add map markers
    for (var i=0; i < $scope.players.length; i++) {
        var player = $scope.players[i];
	var picon = L.icon({
                            'iconUrl': 'data:image/png;base64,' + player.avatar_base64,
                            'iconSize': [32, 32],
                           }
        );
	var marker = L.marker([player.latitude, player.longitude], {
	                                                            'icon': picon
                                                                   }
                             );
        marker.bindPopup("<p>Username: " + player.username + "<br />Name: " + player.name + "</p>");
	marker.addTo(map);
    }
  });
}]);

veripeditusMain.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/register', {
    templateUrl: 'views/register.html',
    controller: 'ViewRegisterController'
  });
}]).controller('ViewRegisterController', ['$scope', 'Player', function($scope, Player) {
  $scope.register = function() {
   // Create and fill Player object
   var player = new Player({
     username: $scope.username,
     name: $scope.name,
     email: $scope.email,
     password: $scope.password,
   });

   // Submit Player object via REST API
   player.$save();
  };
}]);
