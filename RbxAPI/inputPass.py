# -*- coding: utf-8 -*-
"""
Created on Aug 18, 2014

@author: Diana

Custom implmentation of GetPass module to show asterks when you type your password instead of nothing.

It DOES NOT WORK on linux. I can't understand the linux code magic so i didnt try. (i might have tried and broke it)
(idk)(compare to orginial code)


It confused some of the little 9 year old robloxians
*sigh*
"""
import contextlib
import io
import os
import sys
import warnings

from RbxAPI import errors


__all__ = ["getpass", "GetPassWarning", "getnum"]


class GetPassWarning(UserWarning):
    """
    Base class for exceptions.
    """
    # FIXME: why the fuck arfe you hiding in here EXCEPTIONS GO IN ERRORS.PY YOU CUNT
    pass


def win_getpass(prompt = 'Password: ', stream = None):
    """
    Prompt for password with echo off, using Windows getch().

    :param stream: No idea #SorryNotSorry
    :param prompt: What to tell the idiot user.
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


def win_getNum(prompt = '> ', choices = 2, stream = None):
    """
    Select number choices using prompt, up to a max of choices.

    This isnt working correctly with large numbers but it's fine trust me. Just fix it later

    :param stream: No idea.
    :param choices: How many choices
    :param prompt: What to prompt user with
    """
    if sys.stdin is not sys.__stdin__:
        return fallback_getpass(prompt, stream)
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
    return int(num)


def unix_getpass(prompt = 'Password: ', stream = None):
    """
    Prompt for a password, with echo turned off.

    :param stream:
    :param prompt:
    Args:
      prompt: Written on stream to ask for the input.  Default: 'Password: '
      stream: A writable file object to display the prompt.  Defaults to
              the tty.  If no tty is available defaults to sys.stderr.
    Returns:
      The seKr3t input.
    Raises:
      EOFError: If our input tty or stdin was closed.
      GetPassWarning: When we were unable to turn echo off on the input.

    Always restores terminal settings before returning.
    """
    passwd = None
    with contextlib.ExitStack() as stack:
        try:
            # Always try reading and writing directly on the tty first.
            fd = os.open('/dev/tty', os.O_RDWR | os.O_NOCTTY)
            # noinspection PyTypeChecker
            tty = io.FileIO(fd, 'w+')
            stack.enter_context(tty)
            # noinspection PyTypeChecker
            inputt = io.TextIOWrapper(tty)
            stack.enter_context(inputt)
            if not stream:
                stream = inputt
        except OSError:
            # If that fails, see if stdin can be controlled.
            stack.close()
            try:
                fd = sys.stdin.fileno()
            except (AttributeError, ValueError):
                fd = None
                passwd = fallback_getpass(prompt, stream)
            inputt = sys.stdin
            if not stream:
                stream = sys.stderr

        if fd is not None:
            try:
                old = termios.tcgetattr(fd)  # a copy to save
                new = old[:]
                new[3] &= ~termios.ECHO  # 3 == 'lflags'
                tcsetattr_flags = termios.TCSAFLUSH
                if hasattr(termios, 'TCSASOFT'):
                    tcsetattr_flags |= termios.TCSASOFT
                try:
                    termios.tcsetattr(fd, tcsetattr_flags, new)
                    # noinspection PyArgumentList
                    passwd = _raw_input(prompt, stream, input = inputt)
                finally:
                    termios.tcsetattr(fd, tcsetattr_flags, old)
                    stream.flush()  # issue7208
            except termios.error:
                if passwd is not None:
                    # _raw_input succeeded.  The final tcsetattr failed.  Reraise
                    # instead of leaving the terminal in an unknown state.
                    raise
                # We can't control the tty or stdin.  Give up and use normal IO.
                # fallback_getpass() raises an appropriate warning.
                if stream is not inputt:
                    # clean up unused file objects before blocking
                    stack.close()
                passwd = fallback_getpass(prompt, stream)

        stream.write('\n')
        return passwd


def fallback_getpass(prompt = 'Password: ', stream = None):
    """

    :param prompt: Prompt for user
    :param stream: No fucking idea cunt
    :return:
    """
    warnings.warn("Can not control echo on the terminal.", GetPassWarning,
                  stacklevel = 2)
    if not stream:
        stream = sys.stderr
    print("Warning: Password input may be echoed.", file = stream)
    return _raw_input(prompt, stream)


def _raw_input(prompt = "", stream = None, inputt = None):
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
else:
    # getpass = unix_getpass
    raise errors.UnsupportedError()
