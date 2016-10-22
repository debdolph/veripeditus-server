#!/usr/bin/env python3

# veripeditus-server - Server component for the Veripeditus game framework
# Copyright (C) 2016  Dominik George <nik@naturalnet.de>
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

import os
from setuptools import setup

with open('VERSION', 'r') as f:
    version = f.read().strip()

setup(
    name='Veripeditus',
    version=version,
    long_description=__doc__,
    packages=[
              'veripeditus.framework',
              'veripeditus.server',
              'veripeditus.game.test',
             ],
    namespace_packages=[
                        'veripeditus.game',
                       ],
    include_package_data=True,
    package_data={
                  'veripeditus.server': ['data/*'],
                 },
    zip_safe=False,
    install_requires=[
                      'Flask>=0.10',
                      'Flask-Restless==0.17.0',
                      'Flask-SQLAlchemy',
                      'OSMAlchemy',
                      'passlib',
                      'SQLAlchemy-Utils',
                      'Wand',
                     ],
    test_suite='tests',
    entry_points={
                  'console_scripts': [
                                      'veripeditus-standalone = veripeditus.server:server_main'
                                     ]
                 },
)
