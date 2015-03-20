# -*- coding: utf-8 -*-
# ROBLOX Trade Currency bot.
# Copyright (C) 2015  Diana S. Land
# This file is a part of the ROBLOX Trade Currency bot.
# ROBLOX Trade Currency bot. is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# ROBLOX Trade Currency bot. is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with ROBLOX Trade Currency bot.; if not, If not, see <http://www.gnu.org/licenses/> and contact Diana

# Diana may be contacted online at CrazyKilla15@gmail.com
"""
Created on Aug 2, 2014

@author: Diana

Where the magic happens in my TC bot
"""

import ast
import os
import re

from lxml import html

from RbxAPI import general


url = 'http://www.roblox.com/My/Money.aspx'
s = None  # FIXME: global variables are bad. But i guess this has to stay...

os.environ["REQUESTS_CA_BUNDLE"] = os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.pardir, 'cacert.pem'))


def setup():
    """
    Setup the program.

    """
    global s
    s = general.getSession()


def getCash():
    """
    Check how much cash the user has using ROBLOX's API
    May be broken or not. ROBLOX man.

    :return int: 2 variables, containing how much cash the user has.
    """
    r = s.get('http://api.roblox.com/currency/balance')
    val = ast.literal_eval(r.text)
    return int(val['robux']), int(val['tickets'])


def getRate():
    """
    get current market rates using xpath. May need updating a lot if roblox changes theme.

    :return:
    """
    r = s.get(url)
    tree = html.fromstring(r.text)
    rate = tree.xpath('//*[@id="CurrencyQuotePane"]/div[1]/div[2]/div[2]/text()')
    print('Rate is: ' + str(rate))
    m = re.split('/', rate[0])
    print(m)
    return float(m[0]), float(m[1])


def checkTrades():
    """
    Check for active trades.
    May need fixing

    :return bool: True if no trades, False if trades.
    """
    r = s.get(url)
    tree = html.fromstring(r.text)
    tixT = tree.xpath(('//*[@id="ctl00_ctl00_cphRoblox_cphMyRobloxContent_ctl00_OpenBids_Ope'
                       'nBidsUpdatePanel"]/div[1][@class="NoResults"]/text()')
    )
    buxT = tree.xpath(('//*[@id="ctl00_ctl00_cphRoblox_cphMyRobloxContent_ctl00_OpenOffers_OpenOffersUpdatePanel"]'
                       '/div[1][@class="NoResults"]/text()')
    )

    if tixT == [] or buxT == []:
        return False
    return True


def checkRates(t):
    """
    Checks the current trade rates, in future to modify trades.
    Unused.

    :param t: I forget i'm sorry figure out my code.
    :return: no fucking idea.
    """
    if t:
        r = s.get(url)
        tree = html.fromstring(r.text)
        test = tree.xpath('//*[@id="CurrencyBidsPane"]/div/div[1]/text()')
        print(test)
        x = re.split('@', test[0])
        x = re.sub("'r\r\n", '', x[0])
        x = re.sub('\D', '', x)
        print(x)
        return x
    else:
        r = s.get(url)
        tree = html.fromstring(r.text)
        test = tree.xpath('//*[@id="CurrencyOffersPane"]/div/div[1]/span[@class="notranslate"]/text()')
        print(test[0])
        # return x


def getSpread():
    """
    Get the current spread.

    :return: The spread.
    """
    r = s.get(url)
    tree = html.fromstring(r.text)
    spread = tree.xpath("//*[@id='CurrencyQuotePane']/div[1]/div[1]/div[4]/text()")
    print('Spread is: ' + str(spread))
    return spread
