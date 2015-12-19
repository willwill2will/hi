# -*- coding: utf-8 -*-
"""
Project: ROBLOX
File: __init__.py
Author: Diana
Creation Date: 10/19/2014

Copyright (C) 2015  Diana Land
Read LICENSE for more information
"""

# Internal
__author__ = 'Diana'
__version__ = '2.0.3'

import os
import sys

import requests

# Requests, Session. Internal.
Session = requests.session()
Session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0"})

# URLs
TCUrl = "http://www.roblox.com/My/Money.aspx"
CurrencyURL = "http://api.roblox.com/currency/balance"
CheckURL = "http://www.roblox.com/home"
LoginURL = "https://www.roblox.com/newlogin"
EstimateURL = "http://www.roblox.com/Marketplace/EconomyServices.asmx?WSDL"

# Requests CA. Required for freezing. Internal.
if getattr(sys, 'frozen', False):
    os.environ["REQUESTS_CA_BUNDLE"] = os.path.abspath(
        os.path.join(os.path.abspath(sys.argv[0]), os.pardir, "cacert.pem"))

from .inputPass import getnum, getpass, pause
from .general import getValidation, login, listAccounts, loadAccounts, writeConfig, readConfig
from .trade import getSpread, getCash, getRate, checkTrades
