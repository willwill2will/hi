# -*- coding: utf-8 -*-
"""
Project: RbxAPI
File: trade.py
Author: Diana
Creation Date: 8/2/2014

Where the magic happens in my TC bot

Copyright (C) 2016  Diana Land
Read LICENSE for more information
"""

import re
from json import JSONDecodeError
from urllib.error import URLError

from lxml import html
from suds.client import Client

from RbxAPI import CURRENCY_URL, TC_URL, Session, ESTIMATE_URL, DebugLog


def GetCash():
    """
    Check how much cash the user has using ROBLOX's API.
    Requires logged in.

    :return int: Robux, tickets.
    :rtype: int, int
    """
    while True:
        r = Session.get(CURRENCY_URL)
        try:
            val = r.json()
        except JSONDecodeError:
            DebugLog.debug(r.text)
            continue
        break
    return int(val['robux']), int(val['tickets'])


def GetRate():
    """
    Gets the current exchange rates from roblox.

    :return: Rates: Bux, tix.
    :rtype: float, float
    """
    tree = html.fromstring(Session.get(TC_URL).text)
    rate = tree.xpath('//*[@id="CurrencyQuotePane"]/div[1]/div[2]/div[2]/text()')  # Rates
    m = re.split('/', rate[0])
    return float(m[0]), float(m[1])


def IsTradeActive():
    """
    Check for active trades.

    :return bool: True if trade is active. False otherwise.
    :rtype: bool
    """
    tree = html.fromstring(Session.get(TC_URL).text)
    tixT = tree.xpath(('//*[@id="ctl00_ctl00_cphRoblox_cphMyRobloxContent_ctl00_OpenBids_Ope'
                       'nBidsUpdatePanel"]/div[1][@class="NoResults"]/text()'))
    buxT = tree.xpath(('//*[@id="ctl00_ctl00_cphRoblox_cphMyRobloxContent_ctl00_OpenOffers_OpenOffersUpdatePanel"]'
                       '/div[1][@class="NoResults"]/text()'))
    # Default values are ['You do not have any open ____ trades.']
    # So [] means there IS a trade
    if tixT == [] or buxT == []:
        return True
    return False


# noinspection PyUnreachableCode
def CheckRates():
    """
    Checks the current trade rates, in future to modify trades.
    Unused.
    """
    raise NotImplementedError
    if t:
        r = Session.get(TC_URL)
        tree = html.fromstring(r.text)
        test = tree.xpath('//*[@id="CurrencyBidsPane"]/div/div[1]/text()')
        print(test)
        x = re.split('@', test[0])
        x = re.sub("'r\r\n", '', x[0])
        x = re.sub('\D', '', x)
        print(x)
        return x
    else:
        r = Session.get(TC_URL)
        tree = html.fromstring(r.text)
        test = tree.xpath('//*[@id="CurrencyOffersPane"]/div/div[1]/span[@class="notranslate"]/text()')
        print(test[0])
        # return x


def GetSpread():
    """
    Get the current spread.

    :return: The spread.
    :rtype: int
    """
    tree = html.fromstring(Session.get(TC_URL).text)
    spread = tree.xpath("//*[@id='CurrencyQuotePane']/div[1]/div[1]/div[4]/text()")
    return int(spread[0])


def GetTixToBuxEstimate(ticketsToTrade):
    """
    Get the current market estimate for a given value of Tickets to Robux

    :param ticketsToTrade: Amount of Tickets.
    :type ticketsToTrade: int
    :return: The estimated Robux to be received.
    :rtype: int
    """
    client = Client(ESTIMATE_URL)
    try:
        return int(client.service.GetEstimatedTradeReturnForTickets(ticketsToTrade))
    except URLError:
        GetTixToBuxEstimate(ticketsToTrade)


def GetBuxToTixEstimate(robuxToTrade):
    """
    Get the current market estimate for a given value of Robux to Tickets

    :param robuxToTrade: Amount of Robux.
    :type robuxToTrade: int
    :return: The estimated Tickets to be received.
    :rtype: int
    """
    client = Client(ESTIMATE_URL)
    try:
        return int(client.service.GetEstimatedTradeReturnForRobux(robuxToTrade))
    except URLError:
        GetBuxToTixEstimate(robuxToTrade)
