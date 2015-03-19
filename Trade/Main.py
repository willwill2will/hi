# -*- coding: utf-8 -*-
"""
Created on May 18, 2014

@author: Diana

The frontend for my trading bot.

"""
import math
import os
import time
from lxml import html

from colorama import init, deinit, Fore, Style

from RbxAPI import general, trade
from RbxAPI.errors import LoginError, Iaz3Error, SetupError, InvalidException
from RbxAPI.inputPass import getpass, getnum


os.environ["REQUESTS_CA_BUNDLE"] = os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.pardir, 'cacert.pem'))
# os.path.join(os.getcwd(), "cacert.pem")
# FIXME: config is broken. You fix it.
Profit = int(general.readConfig('Data', 'Profit'))  # FIXME: HAHAHA this Profit idea of mine NEVER worked yoyu can fix it LOL
lastTix = int(general.readConfig('Data', 'lastTix'))
lastBux = int(general.readConfig('Data', 'lastBux'))

url = trade.url
s = None
values = { 'ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$OrderType': 'LimitOrderRadioButton',
           'ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$AllowSplitTradesCheckBox': 'on',
           '__EVENTTARGET': 'ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$SubmitTradeButton' }


# noinspection PyUnusedLocal
def cancel(num):
    """
    Cancel trade.
    Doesnt work properly and i never figured out why.

    :param num: Trade number to delete, starting at zero. Currently not used.
    """
    global Profit
    state, event = general.getValidation(url)
    # tra = str(c)  # what to cancel. starts at 0, goes +1
    values2 = {
        'ctl00$ctl00$ScriptManager': ('ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$OpenOffers$OpenOffersUpdat'
                                      'ePanel|ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$OpenOffers$OpenOffers'
                                      'ListView$ctrl0$ctl00$CancelOfferButton'
        ),
        '__EVENTTARGET': ('ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$OpenOffe'
                          'rs$OpenOffersListView$ctrl0$ctl00$CancelOfferButton'
        ),
        '__ASYNCPOST': 'true', '__VIEWSTATE': state, '__EVENTVALIDATION': event }

    values3 = {
        'ctl00$ctl00$ScriptManager': ('ctl00$ctl00$cphRoblox$cphMyRobloxConte'
                                      'nt$ctl00$OpenBids$OpenBidsUpdatePanel|ctl00$ctl00$c'
                                      'phRoblox$cphMyRobloxContent$ctl00$OpenBids$OpenBidsL'
                                      'istView$ctrl0$ctl00$CancelBidButton'
        ),
        '__EVENTTARGET': ('ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl0'
                          '0$OpenBids$OpenBidsListView$ctrl0$ctl00$CancelBidButton'
        ),
        '__ASYNCPOST': 'true', '__VIEWSTATE': state, '__EVENTVALIDATION': event }

    r = s.get(url)
    tree = html.fromstring(r.text)
    Tremain = tree.xpath((
        '//*[@id="ctl00_ctl00_cphRoblox_cphMyRobloxContent_ctl00_OpenBids_OpenBidsU'
        'pdatePanel"]/table/tr[2]/td[2]/text()'))
    Rremain = tree.xpath((
        '//*[@id="ctl00_ctl00_cphRoblox_cphMyRobloxContent_ctl00_OpenOffers_'
        'OpenOffersUpdatePanel"]/table/tr[2]/td[2]/text()'))

    try:
        print('Remaining: ' + str(Rremain[0]))
        Profit -= int(Rremain[0])
    except Exception as ex:
        print(ex)

    s.post(url, data = values2)

    s.post(url, data = values3)


def submit(toTrade, fromC, get, toC):
    """
    Submit a trade to ROBLOX.

    I forgot the variable names and you can figure it out from reading and code usage ok?.

    :param toTrade: I forget.
    :param fromC: Forgot.
    :param get: FOrgot
    :param toC: Forgot
    """
    state, event = general.getValidation(url)
    values['__VIEWSTATE'] = state
    values['__EVENTVALIDATION'] = event
    values['ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$HaveAmountTextBoxRestyle'] = toTrade
    values['ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$HaveCurrencyDropDownList'] = fromC
    values['ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$WantAmountTextBox'] = get
    values['ctl00$ctl00$cphRoblox$cphMyRobloxContent$ctl00$WantCurrencyDropDownList'] = toC

    s.post(url, data = values)


def calculate(w):
    """
    Where the trade/profit "calculation" happens

    BWHAHAHAHAHA this shit SUCKED but everyone else made money from my bot and i never had the patience LOL

    :param w: I... Forgot.
    """
    bux, tix = trade.getCash()
    buxR, tixR = trade.getRate()
    global lastTix
    global lastBux
    global Profit
    if w == 'TixToBux':
        lastTix = tix
        want = tix / (buxR + 0.05)
        want = int(math.ceil(want))
        # if want <= 0: break
        print('Getting: ' + str(want) + ' Bux')
        if want > lastBux:

            print('Robux Profit: ' + str(want - lastBux))

            Profit += want - lastBux

            submit(tix, 'Tickets', want, 'Robux')
            print('submitted')

    elif w == 'BuxToTix':
        lastBux = bux

        want = bux * (tixR - 0.05)
        want = int(math.floor(want))
        print('Getting: ' + str(want) + ' Tix')
        if want > (lastTix + 20):

            print('Tickets Profit: ' + str(want - lastTix))

            submit(bux, 'Robux', want, 'Tickets')
            print('submitted')


def setup():
    # print(colored.COLORS)
    """
    Setup the bot.

    :raise LoginError:
    """
    init()
    global s
    print(Fore.WHITE + '   1: Log In?')
    print(Fore.WHITE + '   2: Load Account?')
    print('\n')

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
                general.login(user, getpass())
                s = general.getSession()
                trade.setup()
                break
    elif choice == 2:
        accounts = general.listAccounts()
        if not accounts:
            raise LoginError('No accounts have been saved, cannot continue.', 2001)
        for acc in accounts:
            print('Accounts:')
            print(Fore.YELLOW + '*  ' + acc)  # @UndefinedVariable
        while True:
            account = input('Log in to: ')
            if account in accounts:
                general.loadAccounts(account)
                s = general.getSession()
                trade.setup()
                break
    elif choice == 3:
        pass
    print(Style.RESET_ALL + " ")  # @UndefinedVariable
    deinit()


while not general.checkInternet():  # FIXME: this bad.
    time.sleep(5)


def main():
    """
    The main function.
    It all starts here

    """
    hour = time.time()
    while 1:
        general.writeConfig({ 'LastBux': lastBux,
                              'LastTix': lastTix,
                              'Profit': Profit
        })
        if (time.time() - hour) >= (60 * 60):
            # FIXME: this profit report never worked right LOL
            hour = time.time()
            print('Hourly Profit Report!')
            print('You have made: ' + str(Profit) + ' Total so far')
            print('____________')

        while not general.checkInternet():  # runs when no internet
            # FIXME: this bad too.
            print('Not Connected')
            time.sleep(5)

        start = time.time()  # @UnusedVariable
        while not (trade.checkTrades()) and general.checkInternet():  # FIXME: this bad too. The check internet.
            print('Wait', end = '\r')
            time.sleep(30)
            end = time.time()
            endtime = end - start
            if endtime >= (60 * 30):
                cancel(0)
                print('Canceled')
                break

        bux, tix = trade.getCash()
        if bux > tix:
            calculate('BuxToTix')
        elif tix > bux:
            calculate('TixToBux')

        print('____________')
        time.sleep(5)

if __name__ == '__main__':
    print('Trade Currency Bot made by Iaz3, offically distrubuted on reddit via MEGA\n BOT IS PROVIDED AS IS'
          '\n IAZ3 NOT LIABLE FOR ANY DAMAGES TO YOUR COMPUTER\n')
    # FIXME: all these try excepts blocks seem pretty bad.
    try:
        setup()
        deinit()
        main()
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass
    except InvalidException:
        raise
    except Iaz3Error as e:
        print(e)
    except Exception as e:
        deinit()
        print(str(e))
        raise
    finally:
        deinit()
        print('Goodbye!')
        os.system('pause')
