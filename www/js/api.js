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
 * MERCHANTAPILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/** global ObjRingbuffer */

angular.module('ngFancyREST', []).factory('APIService', function($log, $window) {
    var metrics = new ObjRingbuffer(100);

    return {
        metrics: metrics
    };
}).factory('APIInterceptor', function($q, $window, APIService) {
    return {
        request: function(request) {
            // Add time of request passing interceptor to determine RTT later
            request.time_send = $window.performance.now();

            return request;
        },
        response: function(response) {
            if ('time_send' in response.config) {
                // Get time of repsonse passing interceptor and determine rtt
                response.config.time_recv = $window.performance.now();

                // Add data to metrics buffer
                APIService.metrics.push({
                    rtt: response.config.time_recv - response.config.time_send
                });
            }

            return response;
        }
    };
});
