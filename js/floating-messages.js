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
 * Service for floating messages
 *
 * This service is a very simple helper implementation to display
 * floating messages to users. It maintains a data structure with
 * (class, message) tuples, with class being any Bootstrap alert class.
 *
 * Messages are added by calling Messages.add("class", "message").
 *
 * Messages can be manually removed by calling Messages.remove(id), e.g.
 * from a dismiss button in the Bootstrap alert.
 *
 * Messages are also given a timeout of 10 seconds, after which they are
 * removed automatically.
 *
 * This snippet, for example, can be used to display the messages:
 *
 *  <div id="floating-messages" class="col-xs-12 col-md-3 col-md-push-9">
 *    <div class="alert alert-{{ msg.class }}" ng-repeat="(id, msg) in Messages.msgs">
 *      <a ng-click="Messages.remove(id)" class="close">&times;</a>
 *      {{ msg.message }}
 *    </div>
 *  </div>
 */
angular.module('ngFloatingMessages', []).factory('Messages', function($timeout) {
    // contains a set of id: {class: 'alert class', message: 'foo'} objects
    var msgs = {}

    // Remove the message
    function remove(id) {
        // Clear the timer first, in case we got called manually
        $timeout.cancel(msgs[id].tid);
        delete msgs[id];
    }

    return {
        // Add a message
        add: function(cls, message) {
            // Find next numeric id
            if (Object.keys(msgs).length > 0) {
                var id = Math.max.apply(null, Object.keys(this.msgs)) + 1;
            } else {
                id = 0;
            }

            // Add desired content with found id
            this.msgs[id] = {
                'class': cls,
                'message': message
            };

            // Add timer to auto-close the message
            var tid = $timeout(remove, 10000, true, id);
            this.msgs[id].tid = tid;
        },
        'remove': remove,
        'msgs': msgs
    };
});
