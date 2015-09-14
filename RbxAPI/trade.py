# -*- coding: utf-8 -*-
"""
Project: ROBLOX
File: party.py
Author: Diana
Creation Date: 8/2/2014

Where the magic happens in my TC bot

Copyright (C) 2015  Diana Land
Read LICENSE for more information
"""

import json
import re

from lxml import html

from RbxAPI import CurrencyURL, TCUrl, Session


def getCash():
    """
    Check how much cash the user has using ROBLOX's API

    :return int: 2 variables, containing how much cash the user has.
    :rtype: int, int
    """
    r = Session.get(CurrencyURL)
    val = json.loads(r.text)
    return int(val['robux']), int(val['tickets'])


def getRate():
    """
    Gets the current exchange rates from roblox.

    Will need updating if ROBLOX changes layout

    :return: Rates
    :rtype: float, float
    """
    r = Session.get(TCUrl)
    tree = html.fromstring(r.text)
    rate = tree.xpath('//*[@id="CurrencyQuotePane"]/div[1]/div[2]/div[2]/text()')  # Rates
    print('Rate is: ' + str(rate))
    m = re.split('/', rate[0])
    print(m)
    return float(m[0]), float(m[1])


def checkTrades():
    """
    Check for active trades.
    If there IS a active Trade, return False.
    Otherwise True

    :return bool: True if no trades, False if trades active.
    :rtype: bool
    """
    r = Session.get(TCUrl)
    tree = html.fromstring(r.text)
    tixT = tree.xpath(('//*[@id="ctl00_ctl00_cphRoblox_cphMyRobloxContent_ctl00_OpenBids_Ope'
                       'nBidsUpdatePanel"]/div[1][@class="NoResults"]/text()'))
    buxT = tree.xpath(('//*[@id="ctl00_ctl00_cphRoblox_cphMyRobloxContent_ctl00_OpenOffers_OpenOffersUpdatePanel"]'
                       '/div[1][@class="NoResults"]/text()'))
    # Default values are ['You do not have any open ____ trades.']
    # So [] means there IS a trade
    if tixT == [] or buxT == []:
        return False
    return True


# noinspection PyUnreachableCode
def checkRates(t):
    """
    Checks the current trade rates, in future to modify trades.
    Unused.

    :param t: I forget i'm sorry figure out my code.
    :return: no fucking idea.
    """
    raise NotImplementedError
    if t:
        r = Session.get(TCUrl)
        tree = html.fromstring(r.text)
        test = tree.xpath('//*[@id="CurrencyBidsPane"]/div/div[1]/text()')
        print(test)
        x = re.split('@', test[0])
        x = re.sub("'r\r\n", '', x[0])
        x = re.sub('\D', '', x)
        print(x)
        return x
    else:
        r = Session.get(TCUrl)
        tree = html.fromstring(r.text)
        test = tree.xpath('//*[@id="CurrencyOffersPane"]/div/div[1]/span[@class="notranslate"]/text()')
        print(test[0])
        # return x


def getSpread():
    """
    Get the current spread.

    :return: The spread.
    :rtype: int
    """
    r = Session.get(TCUrl)
    tree = html.fromstring(r.text)
    spread = tree.xpath("//*[@id='CurrencyQuotePane']/div[1]/div[1]/div[4]/text()")
    print('Spread is: ' + str(spread))
    return int(spread[0])
