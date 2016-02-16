# -*- coding: utf-8 -*-
"""
Project: RbxAPI
File: errors.py
Author: Diana
Creation Date: 8/8/2014

Module containing all errors/exceptions used by the program.

Copyright (C) 2016  Diana Land
Read LICENSE for more information
"""
import os
import sys
import traceback

from RbxAPI import DebugLog


def TracebackHandler(Traceback):
    """
    Handles traceback formatting

    :param Traceback:
    :type Traceback:
    :return:
    :rtype:
    """
    DebugInfo = traceback.extract_tb(Traceback)
    for exc in DebugInfo:
        RealFileName = os.path.basename(os.path.normpath(exc.filename))
        exc.filename = RealFileName
    return ''.join(traceback.format_list(DebugInfo))


def ExcHandler(exception_type, exception, errorTraceback, debug_hook=sys.excepthook):
    """
    Handle proper exceptions being displayed.

    :param exception_type: Type
    :type exception_type: Exception
    :param exception: Exception
    :type exception:
    :param errorTraceback: The traceback of the exception.
    :type errorTraceback: traceback
    :param debug_hook: Backup, is the orginial function
    :type debug_hook: sys.excepthook
    """
    if False:
        debug_hook(exception_type, exception, errorTraceback)
    else:
        Text = "Error: {0} {1}\nTraceback(Send this to Iaz3):\n{2}".format(exception_type.__name__, exception,
                                                                           TracebackHandler(errorTraceback))
        DebugLog.debug("\n\n{0}\n\n".format(Text))
        print(Text)


sys.excepthook = ExcHandler


class RbxAPIError(Exception):
    """
    Base class for all exceptions in RbxAPI
    """

    def __str__(self):
        try:
            return "Error: {0}".format(self.__dict__['message'])
        except KeyError:
            return ""

    def __repr__(self):
        return "<{0}, Error Code: {2}> {1}".format(self.__class__.__name__, self.__dict__ or '')


class NoUsernameError(RbxAPIError):
    """
    Username was not entered.
    """

    def __init__(self):
        self.message = "No Username. Cannot Login."


class StorageError(RbxAPIError):
    """
    An error with the stored account data, possibly corrupt.
    """

    def __init__(self):
        self.message = "Stored data invalid. Please login again."


class AccountsError(RbxAPIError):
    """
    Expired cookie
    """

    def __init__(self):
        self.message = "Invalid/Outdated Username/Password. Account failed to load."


class NoAccountsError(RbxAPIError):
    """
    No accounts were saved.
    """

    def __init(self):
        self.message = "No accounts have been saved, cannot continue."


class SetupError(RbxAPIError):
    """
    An error during setup.
    """

    def __init__(self):
        self.message = "Error During Setup"


class UnsupportedError(RbxAPIError):
    """
    Unsuported operating system.
    """

    def __init__(self):
        self.message = "This operating system is unsuporrted, Sorry!"


class GetPassWarning(UserWarning):
    """
    Base class for exceptions.
    """
    pass
