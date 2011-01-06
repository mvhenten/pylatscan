#!/bin/env python
# PyLatScan - a Laser Triangulation Point Cloud Scanner
#
# Copyright (C) 2010 - 2011 Waag Society <society@waag.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from setuptools import setup, find_packages
setup(
    name = "pylatscan",
    version = "0.11",
    packages = find_packages(),
    #scripts = ['say_hello.py'],
    #install_requires = ['cv'],
    package_data = {
        '': ['*.glade']
    },
    author = "Matthijs van Henten",
    author_email = "matthijs@waag.org",
    description = "This is an Example Package",
    license = "LGPL3.0",
    keywords = "3d scanning 3dscanner laser laser scanner point cloud",
    url = "https://github.com/mvhenten/pylatscan/wiki",   # project home page, if any
    entry_points = {
        'console_scripts': [
            'pylatscan_cli = pylatscan.controller.scanner_cli:main',
            'pylatparse_cli = pylatscan.controller.parser_cli:main',
        ],
        'gui_scripts': [
            'pylatscan = pylatscan.controller.scanner:main',
            'pylatparse = pylatscan.controller.parser:main',
        ]
    }
)
