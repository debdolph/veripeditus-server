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

// Service for floating messages
app.factory('Messages', function($timeout) {
    // contains a set of id: {class: 'alert class', message: 'foo'} objects
    msgs = {}

    function remove(id) {
        // Clear the timer first
        $timeout.cancel(msgs[id].tid);
        delete msgs[id];
    }

    return {
        add: function(cls, message) {
            var id = Math.max.apply(null, Object.keys(msgs)) + 1;
            msgs[id] = {
                'class': cls,
                'message': message
            };

            // Add timer to auto-close the message
            var tid = $timeout(remove, 10000, true, id);
            msgs[id].tid = tid;
        },
        'remove': remove,
        'msgs': msgs
    };
});

app.run(function($rootScope, Messages) {
    $rootScope.Messages = Messages;
});
