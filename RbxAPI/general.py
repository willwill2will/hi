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

General use module. Functions with no specific purpose.

(i had "ast" and "re" imported but unused so be carful)
"""
import configparser
import glob
import os
import pickle
import json

from bs4 import BeautifulSoup
import requests

from RbxAPI import errors

os.environ["REQUESTS_CA_BUNDLE"] = os.path.abspath(os.path.join(os.path.dirname( __file__ ), os.pardir, 'cacert.pem'))

s = requests.session()
s.headers.update({ 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0' })
checkUrl = 'http://www.roblox.com/home'
loginurl = 'https://www.roblox.com/newlogin'

# TODO: Remove these global variables. They bad.
loggedIn = False
LoggedInUser = 'None'


def getIP():
    """
    Gets a user's IP Address

    """
    # May want to IP ban users at some point. Shh top secret.
    return requests.get('http://api.ipify.org').text


def getValidation(url):
    """
    gets validation from webpage for submitting requests

    Works around ROBLOX thingy

    :param url: Url to look at.
    :return: Validation. Returns 2 items.
    """
    r = s.get(url)
    b = BeautifulSoup(r.text)
    viewstate = b.findAll("input", { "type": "hidden", "name": "__VIEWSTATE" })
    eventvalidation = b.findAll('input', { 'type': 'hidden', 'name': '__EVENTVALIDATION' })

    try:
        return viewstate[0]['value'], eventvalidation[0]['value']
    except Exception:
        print(viewstate, eventvalidation)
        raise


def getSession():
    """
    Used to get the current requests session in use by the program.
    This session is used universally by all programs using this API

    :return: Requests Session
    :raise errors.LoginError: Error logging in.
    """
    if loggedIn:
        return s
    else:
        raise errors.LoginError('Failed to load account, cannot continue', 2003)


def listAccounts():
    """
    List the accounts currently saved to disk

    :return: List of accounts
    """
    accounts = []
    for file in glob.glob("*.acc"):
        accounts.append(file.split('.')[0])
    return accounts


def loadAccounts(user):
    """
    Load the specififed account

    :param user: The account to load
    :return: True if success
    """
    global loggedIn
    global s
    with open(str(user) + '.acc', 'rb') as f:
        cookies = pickle.load(f)
        s.cookies = cookies
        s.get(checkUrl)
        print('Cookies Loaded Successfully')
        loggedIn = True
        return True


def login(user, pwd):
    """
    Login into the account

    :param pwd: Password used to login
    :param user: Username used to log in
    """

    global loggedIn
    global LoggedInUser
    if len(user) < 1:
        raise errors.LoginError("Empty Username", 9000)
    with open(str(user) + '.acc', 'wb') as f:
        data = { 'username': user, 'password': pwd }
        s.post(loginurl, data = data)  # login
        s.get(checkUrl)
        if '.ROBLOSECURITY' in s.cookies:
            pickle.dump(s.cookies, f)
            print('Save Successful')
            loggedIn = True
            LoggedInUser = user
            return True
        else:
            f.close()
            os.remove(f.name)
            raise errors.LoginError


def convert(obj):
    """
    Convert javascript things to Python types
    Probably a better way to do it....

    :param obj: Objected to be converted to use Python types
    :return Converted object
    """
    # obj = re.sub('null', 'None', obj)
    # obj = re.sub('false', 'False', obj)
    # obj = re.sub('true', 'True', obj)

    try:
        # return ast.literal_eval(obj)
        # TODO: Make sure this doesnt error out
        return json.loads(obj)  # Should work.
    except SyntaxError:
        # What is this for? I forget...
        return { 'Error': 'The Token Is Invalid.' }


def checkInternet():
    """
    Attempts to check if successfully connected to the internet.

    This is bad and unpythonic and gross.

    :return True or False
    """
    # TODO: Replace with a universal wrapper for requests, with exception handling.
    # That way all connections go through here, and we can catch internet errors. Instead of trying to check before hand
    # it's better and more pythonic.
    try:
        requests.get('http://www.roblox.com')
        return True
    except Exception as e:
        print(e)
        return False


def writeConfig(data):
    """
    Write To the config file.

    :type data: dict
    :param data: Data to go into the Data section. Only accepts string.
    """
    # FIXME: fix this crap. All the configs are broken.
    config = configparser.ConfigParser()

    config[LoggedInUser] = data

    try:
        os.mkdir("%APPDATA%\TcBot")
    except OSError as e:
        print(e)

    with open('%APPDATA%\TCBot\config.ini', 'w') as configfile:
        config.write(configfile)


def readConfig(key):
    """
    Reads from the config file.

    :param key: Find key in section
    :return Key or None
    """
    # FIXME: Fix this fucking shit i broke the configs because they were being shitty and i tried to fix and i give up
    # Sorry not sorry guys
    # if you're reading this i open sourced this you're WELCOME.
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        return config[LoggedInUser][key]
    except KeyError:
        return None
    # return config[LoggedInUser].get(section, key)  # , fallback = fallback)


def getConfig(file = 'config.ini'):
    """
    Returns the config file

    :param file: The file open
    :return config
    """
    # FIXME: COnfigs AGAIN fuck
    config = configparser.ConfigParser()
    config.read(file)
    return config[LoggedInUser]
