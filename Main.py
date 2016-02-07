# -*- coding: utf-8 -*-
"""
Created on May 18, 2014

@author: Diana

The frontend for my trading bot.
"""
import math
import time
import os
import atexit
import sys

from lxml import html
from colorama import init, deinit, Fore, reinit

from RbxAPI import getpass, getnum, getValidation, TCUrl, getCash, getSpread, getRate, login, listAccounts, \
    loadAccounts, writeConfig, readConfig, IsTradeActive, general, pause, Session, getBuxToTixEstimate, \
    getTixToBuxEstimate
from RbxAPI.errors import NoAccountsError, Iaz3Error, SetupError, InvalidException

if getattr(sys, 'frozen', False):
    os.environ["REQUESTS_CA_BUNDLE"] = os.path.abspath(
        os.path.join(os.path.abspath(sys.argv[0]), os.pardir, "cacert.pem"))

Banner = """Trade Currency Bot made by Iaz3, offically distrubuted on reddit/bitbucket via MEGA. BOT IS PROVIDED AS IS.
ROBLOX TCBot version {0}, Copyright (C) 2015 Diana
ROBLOX TCBot comes with ABSOLUTELY NO WARRANTY; for details, refer to the LICENSE file.
This is free software, and you are welcome to redistribute it under certain conditions; read the LICENSE file for details.
"""

values = {
    'ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$OrderType': 'LimitOrderRadioButton',
    'ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$AllowSplitTradesCheckBox': 'on',
    '__EVENTTARGET': 'ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$SubmitTradeButton'
}

version = '2.0.4'


# noinspection PyUnusedLocal,PyUnreachableCode
def cancel(num):
    """
    Cancel trade.
    Doesnt work properly and i never figured out why.

    :param num: Trade number to delete, starting at zero. Currently not used.
    """
    raise NotImplementedError
    state, event = getValidation(TCUrl)
    # tra = str(c)  # what to cancel. starts at 0, goes +1
    values2 = {
        'ctl00$ctl00$ScriptManager': ('ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$OpenOffers$OpenOffersUpdat'
                                      'ePanel|ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$OpenOffers$OpenOffers'
                                      'ListView$ctrl0$ctl00$CancelOfferButton'),
        '__EVENTTARGET': ('ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$OpenOffe'
                          'rs$OpenOffersListView$ctrl0$ctl00$CancelOfferButton'), '__ASYNCPOST': 'true',
        '__VIEWSTATE': state, '__EVENTVALIDATION': event
    }

    values3 = {
        'ctl00$ctl00$ScriptManager': ('ctl00$ctl00$cphRoblox$cphMyRobloxConte'
                                      'nt$ctl00$OpenBids$OpenBidsUpdatePanel|ctl00$ctl00$c'
                                      'phRoblox$cphMyRobloxContent$ctl00$OpenBids$OpenBidsL'
                                      'istView$ctrl0$ctl00$CancelBidButton'),
        '__EVENTTARGET': ('ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl0'
                          '0$OpenBids$OpenBidsListView$ctrl0$ctl00$CancelBidButton'), '__ASYNCPOST': 'true',
        '__VIEWSTATE': state, '__EVENTVALIDATION': event
    }

    r = s.get(TCUrl)
    tree = html.fromstring(r.text)
    Tremain = tree.xpath(('//*[@id="ctl00_ctl00_cphRoblox_cphMyRobloxContent_ctl00_OpenBids_OpenBidsU'
                          'pdatePanel"]/table/tr[2]/td[2]/text()'))
    Rremain = tree.xpath(('//*[@id="ctl00_ctl00_cphRoblox_cphMyRobloxContent_ctl00_OpenOffers_'
                          'OpenOffersUpdatePanel"]/table/tr[2]/td[2]/text()'))
    try:
        print('Remaining: ' + str(Rremain[0]))
    except Exception as ex:
        print(ex)
    s.post(TCUrl, data=values2)
    s.post(TCUrl, data=values3)


def SubmitTrade(toTrade, fromCurrency, AmountReceive, toCurrency, Fast=False):
    """
    Submit a trade to ROBLOX.

    :param toTrade: Money going in, IE to trade
    :type toTrade: int
    :param fromCurrency: Currency you are converting FROM, IE "Robux" or "Tickets"
    :type fromCurrency: str
    :param AmountReceive: What you expect to get in return.
    :type AmountReceive: int
    :param toCurrency: Currency you are convering TO, IE "Tickets" or "Robux"
    :type toCurrency: str
    :param Fast: Whether using FastTrade
    :type Fast: bool
    """
    # If FastTrade, we need to use a Market Order
    if Fast:
        values['ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$OrderType'] = 'MarketOrderRadioButton'
    state, event = getValidation(TCUrl)
    values['__VIEWSTATE'] = state
    values['__EVENTVALIDATION'] = event
    values['ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$HaveAmountTextBoxRestyle'] = toTrade
    values['ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$HaveCurrencyDropDownList'] = fromCurrency
    values['ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$WantAmountTextBox'] = AmountReceive
    values['ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$WantCurrencyDropDownList'] = toCurrency

    Session.post(TCUrl, data=values)


def Calculate():
    """
    Where the trade/profit "calculation" happens
    """
    lastBux, lastTix = getCash()
    while True:
        # waitTime = 0
        while not (IsTradeActive()):
            # waitTime += 1
            # print("Progress {:2.1%}".format(waitTime / 10), end="\r")
            print('Waiting for trade to go through.', end='\r')
            time.sleep(10)
        bux, tix = getCash()  # Money
        buxRate, tixRate = getRate()
        spread = getSpread()
        if (buxRate == 0.0000) or (tixRate == 0.0000) or (abs(buxRate - tixRate) >= 10):
            continue
        # TODO: Very advanced caluclations, using new formula. Focus on tix and bux profit, not net.
        if bux:  # Tix to Bux
            tixWant = int(math.floor(bux / tixRate))
            if tixWant > (lastTix + 20):
                lastTix = tix
                SubmitTrade(bux, "Tickets", tixWant, 'Robux')
                print("Trade Submitted")
        elif tix:
            buxWant = int(math.floor(tix / buxRate))
            tixCost = int(math.ceil(buxWant * buxRate))

            buxProfit = buxWant - lastBux
            tixProfit = lastTix - tixCost

            print("Getting {0} Bux for {1} Tix with "
                  "a potential profit of:\n{2} Robux\n{3} Tickets".format(buxWant, tixCost, buxProfit, tixProfit))

            if buxProfit > lastBux and tixProfit > 0:
                lastBux = bux
                SubmitTrade(tixCost, 'Tickets', buxWant, 'Robux')
                print('Trade Submitted')
        print('____________')
        time.sleep(5)


def FastCalculate(lastTix=None, lastBux=None):
    """
    Fast Trade calculations happen here.

    :param lastBux:
    :type lastBux:
    :param lastTix:
    :type lastTix:
    """
    if lastTix is None and lastBux is None:
        lastTix, lastBux = getCash()
    else:
        lastTix, lastBux = lastTix, lastBux
    while True:
        bux, tix = getCash()
        if bux:  # Bux to Tix.
            lastBux = bux
            want = getBuxToTixEstimate(bux)
            while True:  # Calculates minimum required robux required to get same amount of tix.
                bux -= 1
                if getBuxToTixEstimate(bux) < want:
                    bux += 1
                    break
            GetTix = lastTix + 20  # FIXME: Expand on this, accounting for extra tix made last time.
            if want > GetTix:
                if getBuxToTixEstimate(bux) >= want:  # Make sure still getting the same, correct, amount.
                    print("Getting {0} Tickets".format(want))
                    SubmitTrade(bux, 'Robux', want, 'Tickets', Fast=True)
                else:
                    FastCalculate(lastTix, lastBux)
        elif tix:  # Tix to bux
            lastTix = tix
            want = getTixToBuxEstimate(tix)
            while True:  # Calculates minimum required tickets required to get same amount of robux.
                tix -= 1
                if getTixToBuxEstimate(tix) < want:
                    tix += 1
                    break
            if want > lastBux:
                if getTixToBuxEstimate(tix) >= want:
                    print("Getting {0} Robux".format(want))
                    SubmitTrade(tix, 'Tickets', want, 'Robux', Fast=True)
                else:
                    FastCalculate(lastTix, lastBux)


def _mode():
    """
    What Trading Mode?

    :return: Trading Mode. True means Default. False means FAST.
    :rtype: bool
    """
    reinit()
    print(Fore.WHITE + '   1: Default Trading')
    print(Fore.WHITE + '   2: Fast Trading')
    choice = getnum()
    if choice == 1:
        return True
    elif choice == 2:
        return False
    deinit()


def setup():
    """
    Setup the bot.

    :raises: SetupError, NoAccountsError
    """
    init(convert=True)
    print(Fore.WHITE + '   1: Log In?')
    print(Fore.WHITE + '   2: Load Account?')
    choice = getnum()
    if not choice:
        raise SetupError()
    if choice == 1:
        deinit()
        while True:
            user = input('Username: ')
            if user:
                login(user, getpass())
                break
    elif choice == 2:
        accounts = listAccounts()
        if not accounts:
            raise NoAccountsError()
        for acc in accounts:
            print('Accounts:')
            print(Fore.YELLOW + '*  ' + acc)
        while True:
            account = input('Log in to: ')
            if account in accounts:
                loadAccounts(account)
                break
    deinit()


def main():
    """
    The main function.
    It all starts here
    """
    if _mode():
        Calculate()
    else:  # Fast Trade
        FastCalculate()
        # TODO: Log of trades and profits.
        # FIXME: Somewhere around here it can error,


@atexit.register
def closing():
    """

    :return:
    :rtype:
    """
    deinit()
    pause()


if __name__ == '__main__':
    print(Banner)
    try:
        setup()
        deinit()
        main()
    except KeyboardInterrupt:
        pass
