# -*- coding: utf-8 -*-
"""
Project: ROBLOX
File: errors.py
Author: Diana
Creation Date: 8/8/2014

Module containing all errors/exceptions used by the program.

Copyright (C) 2015  Diana Land
Read LICENSE for more information
"""

import sys


def excHandler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    """
    Handle proper exceptions being displayed.

    :param exception_type:
    :type exception_type:
    :param exception:
    :type exception:
    :param traceback:
    :type traceback:
    :param debug_hook:
    :type debug_hook:
    :return:
    :rtype:
    """
    if False:  # TODO: Add a debug flag?
        debug_hook(exception_type, exception, traceback)
    else:
        print("{0}: {1}".format(exception_type.__name__, exception))


sys.excepthook = excHandler


class Iaz3Error(Exception):
    """
    Base class for exceptions in this module.
    """
    pass


class ConnectError(Iaz3Error):
    """
    Connection Error.
    """

    def __init__(self, message=None):
        """
        :param message: Message to display.
        :type message: str | None
        """
        self.message = message or 'Error 1000: Failed to connect to ROBLOX.com'
        self.errno = 1000

    def __str__(self):
        return self.message

    def __repr__(self):
        return "<{0}> {1}".format(self.__class__.__name__, self.__dict__ or '')


class InvalidException(Iaz3Error):
    """
    Throws when the exception is invalid.
    """

    def __init__(self, msg=None):
        self.msg = msg or 'This exception is the result of an unexpected error. Please contact Iaz3.'
        self.errcode = 5

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "<{0}> {1}".format(self.__class__.__name__, self.__dict__ or '')


class LoginError(Iaz3Error):
    """
    Error logging in.

    :param message: Messagr to display
    :param errno: the error number
    :raise InvalidException: Raises if this exception was not intended, but a program bug.
    """

    def __init__(self, message=None, errno=None):
        self.errno = errno or 2000
        self.message = message or 'Error 2000: Failed to login, cannot continue.'
        self.msg = 'Error {0}: {1}'.format(self.errno, self.message)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "<{0}> {1}".format(self.__class__.__name__, self.__dict__ or '')


class SetupError(Iaz3Error):
    """
    An error during setup.
    """

    def __init__(self):
        pass

    def __str__(self):
        return "There was an error during Setup"

    def __repr__(self):
        return "<{0}> {1}".format(self.__class__.__name__, self.__dict__ or '')


class UnsupportedError(Iaz3Error):
    """
    Unsuported operatign system.
    """

    def __init__(self):
        pass

    def __str__(self):
        return 'This operating system is unsuporrted, Sorry!'

    def __repr__(self):
        return "<{0}> {1}".format(self.__class__.__name__, self.__dict__ or '')


class GetPassWarning(UserWarning):
    """
    Base class for exceptions.
    """
    pass


if __name__ == '__main__':
    pass
