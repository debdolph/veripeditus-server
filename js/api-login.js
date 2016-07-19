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

/*
 * This service provides very basic authentication functionality by
 * using nothing more than HTTP Basic Auth. It makes some assumptions:
 *
 *  1. All HTTP requests go to the same endpoint or, at least, endpints
 *     expecting the same credentials.
 *  2. Endpoints reliably return a status of 401 iff a request needs
 *     authentication or the provided credentials could not be verified.
 *  3. There is an ngRoute matching /login that this service redirects
 *     to when it receives a 401 status.
 *
 * We deliberately decided to not use OAUth, any other token-based or
 * session based authentication or anything else. The strategy of this
 * authentication method is a radicalisation of RESTful combined with
 * the KISS principle - HTTP Basic Auth is well-known, a mature
 * standard, enough to authenticate a client and does not need any other
 * state maintenance on the server or the client.
 *
 * To use the service, all you need to do is create a view, routed to
 * from /login, that, after collecting credentials from the user, calls
 * APIService.login(username, password, remember). If remember is
 * truthy, the authentication string will be stored in localStorage and
 * retrieved on instantiation of the service. If not, it will be stored
 * in sessionStorage in order to survive page reloads. Also, add the
 * interceptor like this:
 *
 *  $httpProvider.interceptors.push('APILoginInterceptor');
 *
 * To get rid of the stored credentials, call APIService.logout().
 *
 * The service also extracts an object called server_info from JSON
 * replies to any HTTP request. The idea is that every REST response
 * conveys information about the server. This removes the need for
 * separate retrieval of that information and allows the application to
 * react to any changes immediately (like API version on updates, easing
 * live migrations).
 *
 * If this server_info object contains an object named user, then this
 * is taken to represent the user authenticated through HTTP Basic auth
 * and is used by the service to determine successful login.
 *
 * The Messages service is used to add floating messages on login,
 * logout or error (optionally, if it is available).
 */

angular.module('ngBasicAuth', []).factory('APIService',
    function($log, $window, $injector) {
        // Try to get Messages service
        var Messages;
        try {
            Messages = $injector.get('Messages');
        } catch(error) {
            $log.warn("APIService: Messages service not available, adding stub.");

            // Add a stub making Messages calls no-op
            Messages = {add: function() {}}
        }

        var server_info = {};

        // Look for auth string in session storage, then local storage
        var auth_string = $window.sessionStorage.auth_string || $window.localStorage.auth_string || "";
        if (auth_string) {
            $log.info("APIService: Loaded known HTTP Basic Auth string");
        }

        return {
            login: function(username, password, remember) {
                // Encode HTTP basic auth string
                this.auth_string = "Basic " + window.btoa(username + ":" + password);

                // Store auth string in session storage
                $window.sessionStorage.auth_string = auth_string;
                // Also store in local persistent storage if desired
                if (remember) {
                    $window.localStorage.auth_string = auth_string;
                }

                $log.log("APIService: Stored new HTTP Basic Auth string");
            },
            logout: function() {
                // Add floating message
                Messages.add('info', 'You have been logged out.');

                // Unset and emove auth string from all storages
                this.auth_string = "";
                delete $window.sessionStorage['auth_string'];
                delete $window.localStorage['auth_string'];

                $log.log("APIService: Removed HTTP Basic Auth string");
            },
            server_info: server_info,
            auth_string: auth_string
        };
    }
).factory('APILoginInterceptor',
    function($q, $location, $rootScope, $log, Messages, APIService) {
        return {
            request: function(request) {
                if (APIService.auth_string) {
                    request.headers.Authorization = APIService.auth_string;
                }

                return request;
            },
            response: function(response) {
                if (typeof response.data === "object" && 'server_info' in response.data) {
                    // Copy server info if it is inside the response
                    // Doing this for every response that has it for live migrations on server-side
                    var new_server_info = angular.copy(angular.fromJson(response.data).server_info);
                }

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
    }
);
