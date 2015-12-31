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
from colorama import init, deinit, Fore

from RbxAPI import getpass, getnum, getValidation, TCUrl, getCash, getSpread, getRate, login, listAccounts, \
    loadAccounts, writeConfig, readConfig, checkTrades, general, pause, Session, getBuxEstimate, getTixEstimate
from RbxAPI.errors import LoginError, Iaz3Error, SetupError, InvalidException

if getattr(sys, 'frozen', False):
    os.environ["REQUESTS_CA_BUNDLE"] = os.path.abspath(
            os.path.join(os.path.abspath(sys.argv[0]), os.pardir, "cacert.pem"))

values = {
    'ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$OrderType': 'LimitOrderRadioButton',
    'ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$AllowSplitTradesCheckBox': 'on',
    '__EVENTTARGET': 'ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$SubmitTradeButton'
}

version = '2.0.3'


# noinspection PyUnusedLocal,PyUnreachableCode
def cancel(num):
    """
    Cancel trade.
    Doesnt work properly and i never figured out why.

    :param num: Trade number to delete, starting at zero. Currently not used.
    """
    raise NotImplementedError
    global Profit
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
        Profit -= int(Rremain[0])
    except Exception as ex:
        print(ex)
    s.post(TCUrl, data=values2)
    s.post(TCUrl, data=values3)


def submit(toTrade, fromCurrency, AmountReceive, toCurrency, Fast=False):
    """
    Submit a trade to ROBLOX.

    :param toTrade: Money going in, IE to trade
    :type toTrade: int
    :param fromCurrency: Currency you are converting FROM, IE "Robux" or "Tickets"
    :type fromCurrency: str
    :param AmountReceive: What you expect to get in return.
    :type AmountReceive: int
    :param toCurrency: Currency you are convering TO, IE "Robux" or "Tickets"
    :type toCurrency: str
    :param Fast:
    :type Fast:
    """
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


def calculate(mode):
    """
    Where the trade/profit "calculation" happens

    :param mode: What direction to calculate
    :type mode: str
    """
    bux, tix = getCash()  # Money
    buxR, tixR = getRate()  # Rates
    spread = getSpread()
    if (buxR == 0.0000) or (tixR == 0.0000):
        return
    if not (spread < 10000) or (spread <= -10000):
        print("Bad spread")
        print("This is experimental. Report problems with it.")
        return
    # TODO: fix spread
    global lastTix
    global lastBux
    global Profit
    if mode == 'TixToBux':
        lastTix = tix
        if spread > 0:
            want = tix / (buxR + 0.05)
        else:
            want = tix / (tixR + 0.05)
        want = int(math.floor(want))
        print('Getting: ' + str(want) + ' Bux')
        if want > lastBux:
            print('Robux Profit: ' + str(want - lastBux))
            Profit += want - lastBux
            submit(tix, 'Tickets', want, 'Robux')
            print('Trade Submitted')
    elif mode == 'BuxToTix':
        lastBux = bux
        if spread > 0:
            want = bux * (tixR - 0.02)
        else:
            want = bux * (buxR - 0.02)
        want = int(math.floor(want))
        print('Getting: ' + str(want) + ' Tix')
        if want > (lastTix + 20):  # 20 profit
            print('Tickets Profit: ' + str(want - lastTix))
            submit(bux, 'Robux', want, 'Tickets')
            print('Trade Submitted')


def FastCalculate():
    """
    Fast Trade calculations happen here.

    :return:
    :rtype:
    """
    global lastTix
    global lastBux
    global Profit
    bux, tix = getCash()
    if bux:  # Bux to Tix.
        lastBux = bux
        want = getBuxEstimate(bux)
        while True:
            bux -= 1
            if getBuxEstimate(bux) < want:
                bux += 1
                break
        if want != getBuxEstimate(bux):
            FastCalculate()
            return
        # FIXME: This doesnt work. LastTix gets overwritten, so yeah?????
        if (lastTix + tix) >= (lastTix + 20):
            GetTix = lastTix + tix
        else:
            GetTix = lastTix + (20 - tix)
        if want > GetTix:
            if getBuxEstimate(bux) == want:
                print("Getting {0} Tickets".format(want))
                submit(bux, 'Robux', want, 'Tickets', Fast=True)
            else:
                FastCalculate()
    elif tix:  # Tix to bux
        lastTix = tix
        want = getTixEstimate(tix)
        while True:
            tix -= 1
            if getTixEstimate(tix) < want:
                tix += 1
                break
        if want != getTixEstimate(tix):
            FastCalculate()
            return
        if want > lastBux:
            if getTixEstimate(tix) == want:
                print("Getting {0} Robux".format(want))
                submit(tix, 'Tickets', want, 'Robux', Fast=True)
            else:
                FastCalculate()


def _mode():
    """
    What Trading Mode?

    :return: Trading Mode. True means Default. False means FAST.
    :rtype: bool
    """
    init()
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

    :raises: SetupError, LoginError
    """
    init(autoreset=True)
    print(Fore.WHITE + '   1: Log In?')
    print(Fore.WHITE + '   2: Load Account?')
    # x = 0
    # x += 1
    # print("Progress {:2.1%}".format(x / 10), end = "\r")
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
            raise LoginError('No accounts have been saved, cannot continue.', 2001)
        for acc in accounts:
            print('Accounts:')
            print(Fore.YELLOW + '*  ' + acc)
        while True:
            account = input('Log in to: ')
            if account in accounts:
                loadAccounts(account)
                break
    deinit()


def main(Mode):
    """
    The main function.
    It all starts here

    :param Mode:
    :type Mode:
    """
    if Mode:
        while 1:
            writeConfig({'LastBux': lastBux, 'LastTix': lastTix, 'Profit': Profit})
            while not (checkTrades()):
                print('Wait', end='\r')
                time.sleep(10)
            bux, tix = getCash()  # Money
            if bux:
                calculate('BuxToTix')
            elif tix:
                calculate('TixToBux')
            print('____________')
            time.sleep(5)
    else:
        while 1:
            writeConfig({'LastBuxFAST': lastBux, 'LastTixFAST': lastTix, 'ProfitFAST': Profit})
            FastCalculate()
            # TODO: Log of trades and profits.
            # FIXME: Somewhere around here it can error,
            print('Wait', end='\r')
            time.sleep(5)


@atexit.register
def closing():
    """

    :return:
    :rtype:
    """
    deinit()
    pause()


if __name__ == '__main__':
    print('Trade Currency Bot made by Iaz3, offically distrubuted on reddit/bitbucket via MEGA. BOT IS PROVIDED AS IS.')
    print("ROBLOX TCBot version " + version + ", Copyright (C) 2015 Diana"
                                              "\nROBLOX TCBot comes with ABSOLUTELY NO WARRANTY; for details, "
                                              "refer to the LICENSE file."
                                              "\nThis is free software, and you are welcome to redistribute it "
                                              "under certain conditions; read the LICENSE file for details.")
    try:
        setup()
        deinit()
        global Profit
        global lastTix
        global lastBux
        if _mode():
            Profit = int(readConfig(general.LoggedInUser, 'Profit'))
            lastTix = int(readConfig(general.LoggedInUser, 'lastTix'))
            lastBux = int(readConfig(general.LoggedInUser, 'lastBux'))
            main(True)
        else:
            Profit = int(readConfig(general.LoggedInUser, 'ProfitFAST'))
            lastTix = int(readConfig(general.LoggedInUser, 'lastTixFAST'))
            lastBux = int(readConfig(general.LoggedInUser, 'lastBuxFAST'))
            main(False)
    except KeyboardInterrupt:
        pass
    except InvalidException:
        raise
    except Iaz3Error as e:
        print(e)
    except Exception as e:
        deinit()
        print(str(e))
        raise
