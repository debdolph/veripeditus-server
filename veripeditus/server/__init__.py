"""
Main server application
"""

# veripeditus-server - Server component for the Veripeditus game framework
# Copyright (C) 2016  Dominik George <nik@naturalnet.de>
# Copyright (c) 2015  Mirko Hoffmann <m.hoffmann@tarent.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import os

from veripeditus.server.app import app

def server_main():
    # parse arguments
    aparser = argparse.ArgumentParser()
    aparser.add_argument("-w", "--webapp", help="path to the webapp files")
    aparser.add_argument("-d", "--debug", help="enable debug in Flask app", action="store_true")
    args = aparser.parse_args()

    if args.debug:
        app.debug = True

    if args.webapp:
        @app.route('/<path:path>')
        def _serve_webapp(path):
            return app.send_static_file(os.path.join(args.webapp, path))

    app.run()

if __name__ == '__main__':
    server_main()
