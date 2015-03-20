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
Created on May 20, 2014

@author: Diana
"""
from cx_Freeze import *
import requests
import msilib

base = None

GUID = msilib.gen_uuid()

shortcut_table = [
    ("DesktopShortcut",  # Shortcut
     "DesktopFolder",  # Directory_
     "Trade Currency Bot",  # Name
     "TARGETDIR",  # Component_
     "[TARGETDIR]TCBot.exe",  # Target
     None,  # Arguments
     None,  # Description
     None,  # Hotkey
     None,  # Icon
     None,  # IconIndex
     None,  # ShowCmd
     'TARGETDIR'  # WkDir
    ),

    ("StartupShortcut",  # Shortcut
     "StartupFolder",  # Directory_
     "Trade Currency Bot",  # Name
     "TARGETDIR",  # Component_
     "[TARGETDIR]TCBot.exe",  # Target
     None,  # Arguments
     None,  # Description
     None,  # Hotkey
     None,  # Icon
     None,  # IconIndex
     None,  # ShowCmd
     'TARGETDIR'  # WkDir
    ),

    ("UninstallShortcut",  # Shortcut
     "DesktopFolder",  # Directory_
     "Uninstall TCBot",  # Name
     "TARGETDIR",  # Component_
     "[SystemFolder]msiexec.exe",  # Target
     "/x " + GUID,  # Arguments
     'Test',  # Description
     None,  # Hotkey
     None,  # Icon
     None,  # IconIndex
     True,  # ShowCmd
     'SystemFolder'  # WkDir
    )

]

msi_data = { "Shortcut": shortcut_table }


build_exe_options = { "include_files": [(requests.certs.where(), 'cacert.pem'), 'TCInfo.txt'],
                      'includes': ['lxml.etree', 'lxml._elementpath', 'gzip', ],
                      'packages': ['os', 'RbxAPI', ],
                      'include_msvcr': True
}

bdist_msi_options = { 'upgrade_code': '{B8086972-1305-4CE4-854D-F050B99DC05C}',
                      'data': msi_data,
                      'product_code': GUID
}

app = Executable("Trade\Main.py",
                 base = base,
                 targetName = 'TCBot.exe',
                 # icon = "TCicon.ico",
)

ver = '2.0'
setup(name = "Trade Currency Bot",
      author = 'Iaz3',
      author_email = 'CrazyKilla15@gmail.com',
      version = ver,
      description = "Iaz3's Trade Currency Bot for Roblox",
      options = { "build_exe": build_exe_options, 'bdist_msi': bdist_msi_options },
      executables = [app]
)

# print('Setup Completed: ' + time.strftime("%m/%d/%Y %I:%M:%S %p", time.localtime()))
