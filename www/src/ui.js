/*
 * veripeditus-web - Web frontend to the veripeditus server
 * Copyright (C) 2016  Dominik George <nik@naturalnet.de>
 * Copyright (C) 2016  Eike Tim Jesinghaus <eike@naturalnet.de>
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

function control_click() {
    var view = $(this).attr("id").substr(8);
    var dialog = $('<div></div>').load("html/views/" + view + ".html");
    // FIXME fix title extraction
    //var head = dialog.children().filter("h1");
    //var title = head.text();
    //dialog.attr("title", title);
    //head.remove();
    dialog.attr("title", view);
    dialog.dialog();

    // UI magic
    if (view == "player") {
        if (localStorage.getItem("username")) {
            dialog.filter("#dialog-player-login").hide();
            dialog.filter("#dialog-player-logout").show();
        } else {
            dialog.filter("#dialog-player-login").show();
            dialog.filter("#dialog-player-logout").hide();
        }
    }
}

$('div.control').on("click", control_click);
