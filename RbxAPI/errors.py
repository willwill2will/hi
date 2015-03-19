# -*- coding: utf-8 -*-
"""
Created on Aug 8, 2014

@author: Diana

Module containing all errors used by the program.
"""


class Iaz3Error(Exception):
    """
    Base class for exceptions in this module.

    """
    pass


class ConnectError(Iaz3Error):
    """

    :param message: Message to display. Can be None.
    """

    def __init__(self, message = None):
        self.message = message or 'Error 1000: Failed to connect to ROBLOX.com'
        self.errno = 1000

    def __str__(self):
        return self.message


class InvalidException(Iaz3Error):
    """
    Throws when the exception is invalid.

    """

    def __init__(self):
        pass

    def __str__(self):
        return 'This exception is the result of an unexpected error. Please contact Iaz3.'


class LoginError(Iaz3Error):
    """
    Error logging in.

    :param message: Messagr to display
    :param errno: the error number
    :raise InvalidException: Raises if this exception was not intended, but a program bug.
    """

    def __init__(self, message = None, errno = None):
        self.errno = errno or 2000
        self.message = message or 'Error 2000: Failed to login, cannot continue.'
        self.msg = 'Error {0}: {1}'.format(self.errno, self.message)
        # Error is there is message and not an error number, or if there is an error number and not a message.
        # If there is one, there has to be the other. Otherwise error.
        # Does format crash on None values? i guess not
        if ((not errno) and message) or (errno and (not message)):
            raise InvalidException

    def __str__(self):
        return self.msg


class SetupError(Iaz3Error):
    """
    An error during setup.

    """

    def __init__(self):
        pass

    def __str__(self):
        return "There was an error during Setup"


class UnsupportedError(Iaz3Error):
    """
    Unsuported operatign system. O.O

    """

    def __init__(self):
        pass

    def __str__(self):
        return 'This operating system is unsuporrted, Sorry!'


if __name__ == '__main__':
    pass

