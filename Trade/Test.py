# -*- coding: utf-8 -*-
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
