/*
 * veripeditus-web - Web frontend to the veripeditus server
 * Copyright (C) 2016  Dominik George <nik@naturalnet.de>
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 * -or-
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

app.factory('APIService', function($log, Messages) {
    var server_info = {};

    // Look for auth string in session storage, then local storage
    var auth_string = sessionStorage.auth_string || localStorage.auth_string || "";
    if (auth_string) {
        $log.info("APIService: Loaded known HTTP Basic Auth string");
    }

    return {
        login: function(username, password, remember) {
            // Encode HTTP basic auth string
            this.auth_string = "Basic " + window.btoa(username + ":" + password);

            // Store auth string in session storage
            sessionStorage.auth_string = auth_string;
            // Also store in local persistent storage if desired
            if (remember) {
                localStorage.auth_string = auth_string;
            }

            $log.log("APIService: Stored new HTTP Basic Auth string");
        },
        logout: function() {
            // Add floating message
            Messages.add('info', 'You have been logged out.');

            // Unset and emove auth string from all storages
            this.auth_string = "";
            delete sessionStorage['auth_string'];
            delete localStorage['auth_string'];

            $log.log("APIService: Removed HTTP Basic Auth string");
        },
        server_info: server_info,
        auth_string: auth_string
    };
});

app.factory('APILoginInterceptor', function($q, $location, $rootScope, $log, Messages, APIService) {
    return {
        request: function(request) {
            if (APIService.auth_string) {
                request.headers.Authorization = APIService.auth_string;
            }

            return request;
        },
        response: function(response) {
            try {
                // Copy server info if it is inside the response
                // Doing this for every response that has it for live migrations on server-side
                var new_server_info = angular.copy(angular.fromJson(response.data).server_info);
            } catch(err) {}

            // Did a user entry appear?
            if (new_server_info) {
                // Get old and new usernames
                var old_user = ('user' in APIService.server_info) && ('username' in APIService.server_info.user) ? APIService.server_info.user.username : "";
                var new_user = ('user' in new_server_info) && ('username' in new_server_info.user) ? new_server_info.user.username : "";

                if (old_user != new_user && new_user != "") {
                    // Obviously we just logged in successfully
                    $log.info("APIService: Successful login with HTTP Basic Auth string");
                    Messages.add('success', 'Login successful.');
                }

                // Store new server info
                APIService.server_info = angular.copy(new_server_info);
            }

            // Return (possibly modified) response
            return response;
        },
        responseError: function(response) {
            if (response.status == 401) {
                $log.warn("APIService: HTTP Basic Auth failed, redirecting to login");

                // Check if we were using authentication
                if (APIService.auth_string) {
                    // If yes, tell user their credentials are wrong
                    Messages.add('danger', 'Login failed.');
                } else {
                    // If not, tell the user they need to log in now
                    Messages.add('info', 'You need to login for this to work.');
                }
                return $location.path("/login");
            }
            return $q.reject(response);
        }
    };
});

app.config(function($httpProvider) {
    // Add a global interceptor that watches for a 401 status
    // and redirects to /login if necessary
    $httpProvider.interceptors.push('APILoginInterceptor');
});

app.run(function($rootScope, APIService) {
    $rootScope.APIService = APIService;
});
