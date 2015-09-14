# -*- coding: utf-8 -*-
"""
Project: ROBLOX
File: inputPass.py
Author: Diana
Creation Date: 8/18/2014

Custom implmentation of GetPass module to show asterks when you type your password instead of nothing.

It DOES NOT WORK on linux. I can't understand the linux code magic so i didnt try.

Copyright (C) 2015  Diana Land
Read LICENSE for more information
"""
import sys
import warnings

from RbxAPI import errors

__all__ = ["getpass", "getnum", "win_pause"]


def win_getpass(prompt='Password: ', stream=None):
    """
    Prompt for password with echo off, using Windows getch().

    :param stream: No idea #SorryNotSorry
    :param prompt: What to display/prompt to the user.
    """
    if sys.stdin is not sys.__stdin__:
        return fallback_getpass(prompt, stream)
    import msvcrt
    for c in prompt:
        msvcrt.putwch(c)
    pw = ""
    while 1:
        c = msvcrt.getwch()
        if c == '\r' or c == '\n':
            break
        if c == '\003':
            break
            # raise KeyboardInterrupt
        if c == '\b':
            if len(pw) > 0:
                pw = pw[:-1]
                msvcrt.putwch('\x08')
                msvcrt.putwch(' ')
                msvcrt.putwch('\x08')
        else:
            msvcrt.putwch('*')
            pw = pw + c
    msvcrt.putwch('\r')
    msvcrt.putwch('\n')
    return pw


def win_getNum(prompt='> ', choices=2, stream=None):
    """
    Select number choices using prompt, up to a max of choices.

    This isnt working correctly with large numbers but it's fine trust me. Just fix it later

    :param stream: No idea.
    :param choices: How many choices
    :type choices: int
    :param prompt: What to prompt user with
    :type prompt: str
    """
    import msvcrt
    for c in prompt:
        msvcrt.putwch(c)
    num = ""
    while 1:
        c = msvcrt.getwch()
        if c == '\r' or c == '\n':
            if num:
                break
        if c == '\003':
            break
            # raise KeyboardInterrupt
        if c == '\b':
            if len(num) > 0:
                num = num[:-1]
                msvcrt.putwch('\x08')
                msvcrt.putwch(' ')
                msvcrt.putwch('\x08')
        else:
            if c.isdigit():
                if int(c) <= choices and len(num) <= 0:
                    msvcrt.putwch(c)
                    num = c
    msvcrt.putwch('\r')
    msvcrt.putwch('\n')
    try:
        return int(num)
    except ValueError:
        return None


def win_pause():
    """
    Stops the program from exiting immediatly.
    """
    import msvcrt
    for c in "Press any key to exit.":
        msvcrt.putwch(c)
    while 1:
        c = msvcrt.getwch()
        if c:
            break
    msvcrt.putwch('\r')
    msvcrt.putwch('\n')


def fallback_getpass(prompt='Password: ', stream=None):
    """

    :param prompt: Prompt for user
    :param stream: No fucking idea
    :return:
    """
    warnings.warn("Can not control echo on the terminal.", errors.GetPassWarning, stacklevel=2)
    if not stream:
        stream = sys.stderr
    print("Warning: Password input may be echoed.", file=stream)
    return _raw_input(prompt, stream)


def _raw_input(prompt="", stream=None, inputt=None):
    # This doesn't save the string in the GNU readline history.
    if not stream:
        stream = sys.stderr
    if not inputt:
        inputt = sys.stdin
    prompt = str(prompt)
    if prompt:
        try:
            stream.write(prompt)
        except UnicodeEncodeError:
            # Use replace error handler to get as much as possible printed.
            prompt = prompt.encode(stream.encoding, 'replace')
            prompt = prompt.decode(stream.encoding)
            stream.write(prompt)
        stream.flush()
    # NOTE: The Python C API calls flockfile() (and unlock) during readline.
    line = inputt.readline()
    if not line:
        raise EOFError
    if line[-1] == '\n':
        line = line[:-1]
    return line


# Bind the name getpass to the appropriate function

try:
    import termios
    # it's possible there is an incompatible termios from the
    # McMillan Installer, make sure we have a UNIX-compatible termios
    var = termios.tcgetattr, termios.tcsetattr
except (ImportError, AttributeError):
    try:
        # noinspection PyUnresolvedReferences
        import msvcrt
    except ImportError:
        getpass = fallback_getpass
    else:
        getpass = win_getpass
        getnum = win_getNum
        pause = win_pause
else:
    # getpass = unix_getpass
    raise errors.UnsupportedError()
