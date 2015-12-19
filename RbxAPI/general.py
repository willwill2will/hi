# -*- coding: utf-8 -*-
"""
Project: ROBLOX
File: general.py
Author: Diana
Creation Date: 8/2/2014

General use module.
Functions that are commonly used among programs are here.

Copyright (C) 2015  Diana Land
Read LICENSE for more information
"""
import configparser
import os
import pickle
import json
import re

from bs4 import BeautifulSoup
import requests

from RbxAPI import errors, Session, CheckURL, LoginURL

# User, Authentication.
LoggedIn = False  # This is ONLY True Or False.
LoggedInUser = None  # This will be a string, containing the username of the user.
# TODO: User Class?


def _SetLoggedIn(value, user=None):
    """
    Internal Function. Dont use.
    Sets whether the User is Logged In or Not.

    :param user: User.
    :type user: str
    :param value: Whether the user is logged in or not
    :type value: bool
    """
    global LoggedIn
    global LoggedInUser
    LoggedIn = value
    if value:
        LoggedInUser = user


def _rbxToken(element):
    """
    Parses HTML for ROBLOX XsrfToken.

    Used by beautiful soup.

    :param element: Element received from Beautiful Soup.
    :type element: BeautifulSoup
    :return: True/False depending on weather element matched.
    :rtype: bool
    """
    if element.name.lower() == "script":
        # FIXME: Make sure the ignore whitespace at beggining works.
        if re.match(r"^\s*Roblox\.XsrfToken\.setToken.*", element.text, re.IGNORECASE):
            return True
    return False


def GetToken():
    """
    Get X-CSRF-TOKEN for use in sending messages/other activies.

    :return: The Token
    :rtype: str
    """
    Token = BeautifulSoup(Session.get('http://www.roblox.com/user.aspx').text, "lxml")
    Token = Token.find_all(_rbxToken)
    Token = re.findall(r"\((.*)\)", Token[0].text)[0]  # FIXME: Will error if Token is broken. It shouldent break,
    # though.
    Token = re.sub("'", '', Token)
    return Token


def getValidation(url):
    """
    gets validation from webpage for submitting requests

    Works around ROBLOX thingy

    :param url: Url to look at.
    :return: Validation. Returns 2 items.
    """
    r = Session.get(url)
    b = BeautifulSoup(r.text, "lxml")
    viewstate = b.findAll("input", {"type": "hidden", "name": "__VIEWSTATE"})
    eventvalidation = b.findAll('input', {'type': 'hidden', 'name': '__EVENTVALIDATION'})
    try:
        return viewstate[0]['value'], eventvalidation[0]['value']
    except Exception:
        raise
        print(viewstate, eventvalidation)
        raise errors.InvalidException


def listAccounts():
    """
    List the accounts currently saved to disk

    :return: List of accounts
    :rtype: list
    """
    accounts = []
    for file in os.scandir(returnPath()):
        if file.is_file() and file.name.endswith('.acc'):
            accounts.append(file.name.split('.')[0])
    return accounts


def loadAccounts(user):
    """
    Load the specififed account

    :param user: The account to load
    :type user: str
    :return: True if success
    :rtype: bool
    """
    user = str(user)
    with open(returnPath(user + '.acc'), 'rb') as f:
        cookies = pickle.load(f)
        Session.cookies = cookies
        r = Session.get(CheckURL)
        if r.url != CheckURL:
            print("Cookies Failed To Load. Please Login Again.")
            raise errors.LoginError("Invalid cookie")
        print('Cookies Loaded Successfully')
        _SetLoggedIn(True, user)
        return True


def login(user, pwd):
    """
    Login into the account

    :param pwd: Password used to login
    :type pwd: str
    :param user: Username used to log in
    :type user: str
    """
    user = str(user)
    if not user:
        raise errors.LoginError("Empty Username", 9000)
    with open(returnPath(user + '.acc'), 'wb') as f:
        data = {'username': user, 'password': pwd}
        Session.post(LoginURL, data=data)  # login
        Session.get(CheckURL)
        if '.ROBLOSECURITY' in Session.cookies:
            pickle.dump(Session.cookies, f)
            print('Save Successful')
            _SetLoggedIn(True, user)
            return True
        else:
            f.close()
            os.remove(f.name)
            raise errors.LoginError("Invalid cookie")


def convert(obj):
    """
    Convert javascript things to Python types
    Probably a better way to do it....

    :param obj: Objected to be converted to use Python types
    :return Converted object
    """
    try:
        # Warning, this will fail if theres a problem with the internet and the page doesnt load correctly.
        # Obj will be bad.
        # FIXME: Implement Checks for this?
        return json.loads(obj)  # Should work.
    except SyntaxError:
        raise


# noinspection PyUnreachableCode
def checkInternet():
    """
    Attempts to check if successfully connected to the internet.

    This is bad and unpythonic and gross.

    :return True or False
    """
    # TODO: Replace with a universal wrapper for requests, with exception handling.
    # That way all connections go through here, and we can catch internet errors. Instead of trying to check before hand
    # it's better and more pythonic.
    raise NotImplementedError
    try:
        requests.get('http://www.roblox.com')
        return True
    except Exception as e:
        print(e)
        return False


def returnPath(file=None):
    """
    Returns the path used for Data Storage.

    :param file: File to create path to. May or may not exist. optional.
    :type file: str
    :return: Path
    :rtype: str
    """
    # Windows only
    path = os.path.abspath(os.path.join(os.getenv("APPDATA"), "Iaz3Programs", "TCBot"))
    if not os.path.isdir(path):
        os.makedirs(path)
    if file:
        return os.path.join(path, file)
    if not file:
        return path


def writeConfig(data):
    """
    Write config file.

    :param data: Data
    :type data: dict
    """
    if not LoggedInUser and LoggedIn:
        raise errors.InvalidException
    config = configparser.ConfigParser()
    config[LoggedInUser] = data
    with open(returnPath('config.ini'), 'w') as configfile:
        config.write(configfile)
        configfile.close()


def readConfig(user, key):
    """
    Read from config file.

    :param user: User's Data to access
    :type user: str
    :param key: Key/Value to retrieve
    :type key: str
    :return: Value requested, so far only int values.
    :rtype: int
    """
    if not LoggedIn:
        raise errors.InvalidException("Not Logged In.")
    config = configparser.ConfigParser()
    config.read(returnPath('config.ini'))
    if user in config:  # Previously saved config.
        userData = config[user]
        return userData.get(key, 0)
    else:  # No existing config file, currently logged in.
        return 0
