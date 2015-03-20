# -*- coding: utf-8 -*-
# ROBLOX Trade Currency bot.
# Copyright (C) 2015  Diana S. Land

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Diana may be contacted online at CrazyKilla15@gmail.com
"""
Project: ROBLOX
File: Test
Author: Diana
Creation Date: 10/19/2014

I attempted to create a test to make sure teh bot worked right. Mainly if the config worked.

Maybe you can get it to work, mr source reader.
"""

__author__ = 'Diana'

import unittest
from RbxAPI import general


class GeneralTest(unittest.TestCase):
    def test_config(self):
        write = { 'LastBux': '046846',
                  'LastTix': '0u58',
                  'Profit': '199'
        }
        general.writeConfig(write)
        value = general.readConfig('Profit')
        print(value)
        config = general.getConfig()
        for f in write:
            self.assertTrue(f in config)
        self.assertEqual(config['Profit'], write['Profit'])
        self.assertEqual(config['LastTix'], write['LastTix'])
        self.assertEqual(config['LastBux'], write['LastBux'])


if __name__ == '__main__':
    unittest.main()
