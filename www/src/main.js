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

Veripeditus = {
    version: '1.0.0a0.dev0',
    views: [],
    registerView: function(view) {
        this.views.push(view);
        if (! this.currentView) {
            this.currentView = view;
        }
    },
    nextView: function() {
        var i = this.views.indexOf(this.currentView);
        i++;
        if (i == this.views.length) {
            i = 0;
        }
        this.currentView.deactivate();
        this.currentView = this.views[i];
        this.currentView.activate();
    },
    currentView: undefined,
    debug: true
};

// Uncomment to enable debugging in webapp
Veripeditus.debug = true;
