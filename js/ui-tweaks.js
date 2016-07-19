/*
 * veripeditus-web - Web frontend to the veripeditus server
 * Copyright (C) 2016  Dominik George <nik@naturalnet.de>
 * Copyright (C) 2016  mirabilos <m@mirbsd.org>
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

$(function() {
    // Used to automatically restyle content area when window size changes,
    // because that might resize the header and footer areas as well
    var resizeFunction = function() {
        // Get heights of header and footer
        var header = document.getElementById("navbar-header").offsetHeight;
        var footer = document.getElementById("footer").offsetHeight;

        // Hide footer if display is too small
        if ($(window).height() < header * 6) {
            $("#footer").hide();
            footer = 0;
        } else {
            $("#footer").show();
        }

        // Update top and height style attributes of outer container to
        // fit in between header and footer
        $("#content-outer").css("top", header).height($(window).height() - header - footer);
    };

    // Initially call resizing code once
    resizeFunction();
    // Subscribe to window resize event
    $(window).on('resize', resizeFunction);

    // Collapse navbar on menu click
    $('.nav a').click(function() {
        $('.navbar-collapse').collapse('hide');
    });
});
