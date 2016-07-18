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

app.factory('APIService', function($http, Messages) {
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

// FIXME This sure needs to be overhauled.
app.factory('APILoginInterceptor', function($location, $rootScope) {
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

app.config(function($httpProvider) {
  // Add a global interceptor that watches for a 401 status
  // and redirects to /login if necessary
  $httpProvider.interceptors.push('APILoginInterceptor');
});

app.run(function($http) {
  // Look for auth string in session storage, then local storage
  var s_auth_string = sessionStorage.auth_string || localStorage.auth_string;
  // Set to HTTP service if auth string was stored
  if (s_auth_string) {
    $http.defaults.headers.common['Authorization'] = s_auth_string;
  }
});
