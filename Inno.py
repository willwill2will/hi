# -*- coding: utf-8 -*-
# !/usr/bin/env python3
"""
Project: RbxAPI
File: Inoo
Author: Diana
Creation Date: 2/8/2016
Creation Time: 7:46 PM
"""

__author__ = 'Diana'

import codecs
import ctypes
import os
import platform
import re
import subprocess
import sys
import sysconfig
import uuid
import winreg
from distutils import command
from zipfile import (ZipFile, ZIP_DEFLATED)

from cx_Freeze.dist import build_exe

command.__all__.append('innosetup')
sys.modules['distutils.command.innosetup'] = sys.modules[__name__]

DEFAULT_ISS = ""
DEFAULT_CODES = """
procedure ExecIfExists(const FileName, Arg: String);
var
    ret: Integer;
begin
    FileName := ExpandConstant(FileName);
    if FileExists(FileName) then begin
        if not Exec(FileName, Arg, '', SW_HIDE, ewWaitUntilTerminated, ret) then
            RaiseException('error: ' + FileName + ' ' + Arg);
    end;
end;
procedure UnregisterPywin32Service(const FileName: String);
begin
    try
        ExecIfExists(FileName, 'stop');
    except
        //already stopped or stop error
    end;
    ExecIfExists(FileName, 'remove');
end;
procedure UnregisterServerIfExists(const FileName: String);
begin
    FileName := ExpandConstant(FileName);
    if FileExists(FileName) then begin
        if not UnregisterServer(%(x64)s, FileName, False) then
            RaiseException('error: unregister ' + FileName);
    end;
end;
""" % {'x64': platform.machine() == 'AMD64',}


def modname(handle):
    """
    get module filename from HMODULE

    :param handle: Windows Handle
    :type handle: int
    """
    b = ctypes.create_unicode_buffer('', 1024)
    ctypes.windll.kernel32.GetModuleFileNameW(handle, b, 1024)
    return b.value


hkshortnames = {
    'HKLM': winreg.HKEY_LOCAL_MACHINE, 'HKCU': winreg.HKEY_CURRENT_USER, 'HKCR': winreg.HKEY_CLASSES_ROOT,
    'HKU': winreg.HKEY_USERS, 'HKCC': winreg.HKEY_CURRENT_CONFIG, 'HKDD': winreg.HKEY_DYN_DATA,
    'HKPD': winreg.HKEY_PERFORMANCE_DATA,
}


def getregvalue(path, default=None):
    """
    Get a registry value

    No Name value

    >>> getregvalue('HKEY_CLASSES_ROOT\\.py')
    'Python.File'

    Named value

    >>> getregvalue('HKEY_CLASSES_ROOT\\.py\\Content Type')
    ''text/plain

    :param path: Reg path
    :type path: str
    :param default: default key
    :type default: bool | str
    """
    root, subkey = path.split('\\', 1)
    if root.startswith('HKEY_'):
        root = getattr(_winreg, root)
    elif root in hkshortnames:
        root = hkshortnames[root]
    else:
        root = winreg.HKEY_CURRENT_USER
        subkey = path

    subkey, name = subkey.rsplit('\\', 1)

    try:
        handle = winreg.OpenKey(root, subkey)
        value, typeid = winreg.QueryValueEx(handle, name)
        return value
    except EnvironmentError:
        return default


class IssFile:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        self.fileObj = open(*self.args, **self.kwargs)
        return self.fileObj

    def __exit__(self, *_):
        self.fileObj.close()


def issline(fileObj, **kwargs):
    noescape = ['Flags', ]
    args = []
    for k, v in list(kwargs.items()):
        if k not in noescape:
            # ' -> ''
            v = '"{0}"'.format(v)
        args.append('%s: %s' % (k, v,))
    fileObj.write(('; '.join(args) + '\n').encode())


class InnoScript(object):
    consts_map = dict(AppName='%(name)s', AppVerName='%(name)s %(version)s', AppVersion='%(version)s',
                      VersionInfoVersion='%(version)s', AppCopyright='%(author)s', AppContact='%(author_email)s',
                      AppComments='%(description)s', AppPublisher='%(author)s', AppPublisherURL='%(url)s',
                      AppSupportURL='%(url)s', )
    metadata_map = dict(SolidCompression='yes', DefaultGroupName='%(name)s', DefaultDirName='{pf}\\%(name)s',
                        OutputBaseFilename='%(name)s-%(version)s-' + str(sysconfig.get_platform()) + '-setup', )
    metadata_map.update(consts_map)
    required_sections = ('Setup', 'Files', 'Run', 'UninstallRun', 'Languages', 'Icons', 'Code',)
    default_flags = ('ignoreversion', 'overwritereadonly', 'uninsremovereadonly',)
    default_dir_flags = ('recursesubdirs', 'createallsubdirs',)
    bin_exts = ('.exe', '.dll', '.pyd',)
    iss_metadata = {}

    def __init__(self, builder):
        self.builder = builder
        self.issfile = os.path.join(self.builder.dist_dir, 'distutils.iss')

    def parse_iss(self, s):
        firstline = ''
        sectionname = ''
        lines = []
        for line in s.splitlines():
            if line.startswith('[') and ']' in line:
                if lines:
                    yield firstline, sectionname, lines
                firstline = line
                sectionname = line[1:line.index(']')].strip()
                lines = []
            else:
                lines.append(line)
        if lines:
            yield firstline, sectionname, lines

    def chop(self, filename, dirname=''):
        """get relative path"""
        if not dirname:
            dirname = self.builder.dist_dir
        if not dirname[-1] in "\\/":
            dirname += "\\"
        if filename.startswith(dirname):
            filename = filename[len(dirname):]
        # else:
        #    filename = os.path.basename(filename)
        return filename

    @property
    def metadata(self):
        metadata = dict((k, v or '') for k, v in list(self.builder.distribution.metadata.__dict__.items()))
        return metadata

    @property
    def AppId(self):
        m = self.metadata
        if m['url']:
            src = m['url']
        elif m['name'] and m['version'] and m['author_email']:
            src = 'mailto:%(author_email)s?subject=%(name)s-%(version).1s' % m
        elif m['name'] and m['author_email']:
            src = 'mailto:%(author_email)s?subject=%(name)s' % m
        else:
            return m['name']
        appid = uuid.uuid5(uuid.NAMESPACE_URL, src).urn.rsplit(':', 1)[1]
        return '{{%s}' % appid

    @property
    def iss_consts(self):
        metadata = self.metadata
        return dict((k, v % metadata) for k, v in list(self.consts_map.items()))

    @property
    def innoexepath(self):
        if self.builder.inno_setup_exe:
            return self.builder.inno_setup_exe

        result = getregvalue('HKCR\\InnoSetupScriptFile\\shell\\compile\\command\\')
        if result:
            if result.startswith('"'):
                result = result[1:].split('"', 1)[0]
            else:
                result = result.split()[0]
            return result

        result = getregvalue('HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion'
                             '\\Uninstall\\Inno Setup 5_is1\\InstallLocation')
        if result:
            return os.path.join(result, 'Compil32.exe')

        result = getregvalue('HKLM\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows'
                             '\\CurrentVersion\\Uninstall\\Inno Setup 5_is1\\InstallLocation')
        if result:
            return os.path.join(result, 'Compil32.exe')

        return ''

    def handle_iss(self, lines, fp):
        for line in lines:
            fp.write(line.encode() + b'\n')

    def handle_iss_setup(self, lines, fp):
        metadata = self.metadata
        iss_metadata = dict((k, v % metadata) for k, v in list(self.metadata_map.items()))
        iss_metadata['OutputDir'] = "."  # self.builder.dist_dir
        iss_metadata['AppId'] = self.AppId

        # if self.builder.service_exe_files or self.builder.comserver_files:
        #     iss_metadata['PrivilegesRequired'] = 'admin'

        # add InfoBeforeFile
        for filename in ('README', 'README.txt', "README.MD"):
            if os.path.isfile(filename):
                iss_metadata['InfoBeforeFile'] = os.path.abspath(filename)
                break

        # add LicenseFile
        for filename in ('license.txt', 'COPYING', "LICENSE"):
            if os.path.isfile(filename):
                iss_metadata['LicenseFile'] = os.path.abspath(filename)
                break

        # handle user operations
        user = {}
        for line in lines:
            m = re.match('\s*(\w+)\s*=\s*(.*)\s*', line)
            if m:
                name, value = m.groups()
                if name in iss_metadata:
                    del iss_metadata[name]
                user[name] = value
                fp.write('%s=%s\n' % (name, value,))
            else:
                fp.write(line + '\n')

        if 'AppId' in iss_metadata:
            print(('There is no "AppId" in "[Setup]" section.\n'
                   '"AppId" is automatically generated from metadata (%s),'
                   'not a random value.' % iss_metadata['AppId']))

        for k in sorted(iss_metadata):
            fp.write(('%s=%s\n' % (k, iss_metadata[k],)).encode('utf_8'))

        self.iss_metadata = {}
        self.iss_metadata.update(iss_metadata)
        self.iss_metadata.update(user)

        fp.write(b'\n')

    def handle_iss_files(self, lines, fp):
        files = []
        excludes = []

        files.extend(self.builder.include_files)
        files.extend([os.path.join("..", self.builder.build_exe)])

        # handle Tkinter
        if 'Tkinter' in self.builder.includes:
            tcl_dst_dir = os.path.join(self.builder.lib_dir, 'tcl')
            files.append(tcl_dst_dir)

        stored = set()
        for filename in files:
            if type(filename) == tuple:
                filename = filename[0]
            if filename in excludes:
                continue
            relname = self.chop(filename)
            # user operation given or already wrote
            if relname in ''.join(lines) or relname in stored:
                continue

            flags = list(self.default_flags)
            place = ''

            if os.path.isfile(filename):
                if os.path.splitext(relname)[1].lower() in self.bin_exts:
                    flags.append('restartreplace')
                    flags.append('uninsrestartdelete')

                if filename.startswith(self.builder.dist_dir):
                    place = os.path.dirname(relname)

                extraargs = {}
            else:
                # isdir
                if filename.startswith(self.builder.dist_dir):
                    place = relname
                relname += '\\*'
                flags.extend(self.default_dir_flags)

            issline(fp, Source=relname, DestDir="{app}\\%s" % place, Flags=' '.join(flags), **extraargs)
            stored.add(relname)

        self.handle_iss(lines, fp)

    def _iter_bin_files(self, attrname, lines=None):
        if lines is None:
            lines = []
        for filename in getattr(self.builder, attrname, []):
            if type(filename) == tuple:
                filename = filename[0]  # FIXME: here
            relname = self.chop(filename)
            if relname in ''.join(lines):
                continue
            yield filename, relname

    def handle_iss_run(self, lines, fp):
        self.handle_iss(lines, fp)

    def handle_iss_uninstallrun(self, lines, fp):
        self.handle_iss(lines, fp)

    def handle_iss_icons(self, lines, fp):
        self.handle_iss(lines, fp)
        for _, filename in self._iter_bin_files('include_files', lines):
            issline(fp, Name="{group}\\%s" % self.metadata['name'], Filename="{app}\\%s" % filename, )

    def handle_iss_languages(self, lines, fp):
        self.handle_iss(lines, fp)
        if lines:
            return
        innopath = os.path.dirname(self.innoexepath)
        for root, dirs, files in os.walk(innopath):
            for basename in files:
                if not basename.lower().endswith('.isl'):
                    continue
                filename = self.chop(os.path.join(root, basename), innopath)
                issline(fp, Name=os.path.splitext(basename)[0], MessagesFile="compiler:%s" % filename, )

    def handle_iss_code(self, lines, fp):
        self.handle_iss(lines, fp)
        fp.write(DEFAULT_CODES.encode())

    def create(self):
        inno_script = os.path.join(os.path.dirname(self.builder.dist_dir), self.builder.inno_script)
        if os.path.isfile(inno_script):
            inno_script = open(inno_script).read()
        else:
            inno_script = self.builder.inno_script

        with IssFile(self.issfile, 'wb') as fp:
            fp.write(codecs.BOM_UTF8)
            fp.write(b'; This file is created by distutils InnoSetup extension.\n')

            # write "#define CONSTANT value"
            consts = self.iss_consts
            consts.update({
                'PYTHON_VERION': '%d.%d' % sys.version_info[:2], 'PYTHON_VER': '%d%d' % sys.version_info[:2],
                'PYTHON_DIR': sys.prefix, 'PYTHON_DLL': modname(sys.dllhandle),
            })
            consts.update((k.upper(), v) for k, v in list(self.metadata.items()))
            for k in sorted(consts):
                fp.write(('#define %s "%s"\n' % (k, consts[k],)).encode('utf_8'))

            fp.write(b'\n')

            # handle sections
            sections = set()
            # FIXME: This is never used??
            for firstline, name, lines in self.parse_iss(inno_script):
                if firstline:
                    fp.write(firstline.encode() + b'\n')
                handler = getattr(self, 'handle_iss_%s' % name.lower(), self.handle_iss)
                handler(lines, fp)
                fp.write(b'\n')
                sections.add(name)

            for name in self.required_sections:
                if name not in sections:
                    fp.write('[{0}]\n'.format(name).encode())
                    handler = getattr(self, 'handle_iss_%s' % name.lower())
                    handler([], fp)
                    fp.write(b'\n')

    def compile(self):
        subprocess.call([self.innoexepath, '/cc', self.issfile])
        outputdir = self.iss_metadata.get('OutputDir', os.path.join(os.path.dirname(self.issfile), 'Output'))
        setupfile = os.path.join(outputdir, self.iss_metadata.get('OutputBaseFilename', 'setup') + '.exe')

        # zip the setup file
        if self.builder.zip:
            if isinstance(self.builder.zip, str):
                zipname = self.builder.zip
            else:
                zipname = setupfile + '.zip'

            zip = ZipFile(zipname, 'w', ZIP_DEFLATED)
            zip.write(setupfile, os.path.basename(setupfile))
            zip.close()

            self.builder.distribution.dist_files.append(('innosetup', '', zipname))
        else:
            self.builder.distribution.dist_files.append(('innosetup', '', setupfile))


class innosetup(build_exe):
    # setup()'s argument is in self.distribution.
    user_options = [('inno-setup-exe=', None, 'a path to InnoSetup exe file (Compil32.exe)'),
                    ('inno-script=', None, 'a path to InnoSetup script file or an InnoSetup script string'),
                    ('bundle-vcr=', None, 'bundle msvc*XX.dll and mfc*.dll and their manifest files'),
                    ('zip=', None, 'zip setup file'), ]
    description = 'create an executable file and an installer by InnoSetup'

    def initialize_options(self):
        options = dict(self.distribution.command_options.get('build_exe', {}))
        options.update(self.distribution.command_options.get('innosetup', {}))
        self.distribution.command_options['innosetup'] = options

        build_exe.initialize_options(self)
        self.inno_setup_exe = ''
        self.inno_script = ''
        self.zip = False
        self.dist_dir = 'dist/'
        os.makedirs(self.dist_dir, exist_ok=True)

    def finalize_options(self):
        build_exe.finalize_options(self)

    def run(self):
        build_exe.run(self)

        script = InnoScript(self)
        # print "*** creating the inno setup script ***"
        script.create()
        # print "*** compiling the inno setup script ***"
        script.compile()
