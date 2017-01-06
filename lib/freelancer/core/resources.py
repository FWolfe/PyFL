# -*- coding: utf-8 -*-

# =============================================================================
#
#    Copyright (C) 2016  Fenris_Wolf, YSPStudios
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =============================================================================

"""
    freelancer.core.resources - Functions for manipulating resource files
    (ids_name and ids_info).

    There are 2 methods of doing this, directly accessing the .dll files,
    or reading .frc files created using Adoxa's resource extraction tools:
    res2frc.exe and frc.exe (prefered method).  Adoxa's tools are a better
    option as it currently has more features like the ability to write changes,
    and is partially cross-platform: dll method requires windows, frc files are
    just text, though creating frc files from dlls and updating changes wont
    work in linux.

    DllFile and FrcFile objects both behave slightly different:
    DllFile:
        *read only access (for now)
        *locks resource .dlls open (you cant modify with other tools while running)
        *loads strings into memory on request
    FrcFiles:
        *full read/write access
        *loads all resources into memory on start
"""
from os.path import join, exists, splitext
import re

try:
    import win32api as w32
    import pywintypes
except ImportError:
    pass

from freelancer.core import settings, log, tools
from freelancer.files.ini import IniSection

BLOCK_RE = re.compile(r'^([SH]) ([0-9]+)(?: (~))?(?:\W+(.+))?$')
EOL_RE = re.compile('(?:\r\n|\r)')
COMMENT_RE = re.compile(r'^\W*;')

_MAXI = 65536
files = []
s_general = None
s_resources = None
method = None


def ids_file_index(ids):
    """ids_file_index(ids)
    converts a ids number into a resource file index and position.
    return a tuple(index, position)

    eg: ids_file_index(10) returns (0, 10) - the 10th entry in resource.dll
    ids_file_index(70000) returns (1, 4464) - the 4464th entry in InfoCards.dll
    """
    # ids might be None depending on the fl data and script
    # so exit gracefully
    if ids is None:
        return None, None
    ids = int(ids) # might be string version of a int, exception on failure
    return ids/_MAXI, ids % _MAXI


def ids_name(ids):
    """ids_name(ids)
    Returns the ids name (string) for the given ids number, or None
    If ids is a IniSection object, attempts to find the ids_name key.
    """
    if isinstance(ids, IniSection):
        ids = ids.get('ids_name', 0, dtype=int)
    ids = int(ids)
    index, _ = ids_file_index(ids)
    return files[index].ids_name(ids)


def ids_info(ids):
    """ids_info(ids)
    Returns the ids info (xml) for the given ids number, or None
    If ids is a IniSection object, attempts to find the ids_info key.
    """
    if isinstance(ids, IniSection):
        ids = ids.get('ids_info', 0, dtype=int)
    ids = int(ids)
    index, _ = ids_file_index(ids)
    return files[index].ids_info(ids)


def find_empty(start, stop, step=1):
    """find_empty(start, stop, step=1)
    Finds and returns the next empty unused ids number within the given range.
    """
    for ids in xrange(start, stop, step):
        index, pos = ids_file_index(ids)
        if method == 'FRC':
            pos = ids
        if files[index].get(pos) == (None, None):
            return ids
    return 0

def load(dllnames):
    """load(dllnames)
    Loads a list of resource dll names
    """
    global s_general, s_resources, method
    s_general = settings.general
    s_resources = settings.resources
    method = s_resources.get('method', 'FRC').upper()
    dllnames = [x[:-4] for x in dllnames]
    rclass = None
    if method == 'FRC':
        log.info('Loading Resources using .frc files')
        rclass = FrcFile
    else:
        log.info('Loading Resources using .dll files')
        rclass = DllFile

    for index, dll in enumerate(dllnames):
        files.append(rclass(dll, index))


def extract_frc_files(dllnames):
    """extract_frc_files(dllnames)
    If adoxa's res2frc.exe is installed, will create .frc files from the .dlls
    """
    for index, name in enumerate(dllnames):
        name = splitext(name)[0]
        tools.extract_frc(name, index)


def compile_frcs(dllnames):
    """extract_frc_files(dllnames)
    If adoxa's frc.exe is installed, will compile the .frc files into the mod's
    .dll files
    """
    for name in dllnames:
        name = splitext(name)[0]
        tools.compile_frc(name)



#==============================================================================
#
#==============================================================================
class ResourceError(Exception):
    def __init__(self, message):
        log.error(message)

#==============================================================================
#
#==============================================================================
class ResourceFile(object):
    """ReourceFile(name, index)
    Abstract class representing a resource file. This should never be used
    directly. Use DllFile or FrcFile instead"""
    def __init__(self, name, index):
        self.name = name
        self.index = index
        log.debug('Loading Resource File: %s' % name)


    def get(self, ids):
        """get(self, ids)
        Abstract method to be overwritten.
        """
        raise NotImplementedError


    def add(self, ids_data, replace=False):
        """add(self, ids_data, replace=False)
        Abstract method to be overwritten.
        """
        raise NotImplementedError

    def write(self):
        """write(selfs)
        Abstract method to be overwritten.
        """
        raise NotImplementedError

#==============================================================================
#
#==============================================================================
class DllFile(ResourceFile):
    """DllFile(name, index)
    Object representing a resource .dll. This is the least prefered method:
    requires win32api, read-only access
    """
    def __init__(self, name, index):
        ResourceFile.__init__(self, name, index)
        filename = "%s.dll" % join(s_general['path'], 'EXE', self.name)
        # pylint: disable=E1101
        if not exists(filename):
            raise ResourceError('Resource File Missing: %s' % filename)
        try:
            self._dll = w32.LoadLibrary(filename)
        except pywintypes.error:
            raise ResourceError('Failed to load Resource: %s' % filename)

    def get(self, ids):
        """get(self, ids)
        Returns the string and html resources for the specified ids as a
        tuple(string, string)
        """
        ids = ids % _MAXI
        # pylint: disable=E1101
        try:
            string = w32.LoadString(self._dll, ids)
        except pywintypes.error:
            string = None
        try:
            html = unicode(w32.LoadResource(self._dll, 23, ids, 1033), encoding='UTF-16')
        except pywintypes.error:
            html = None
        return string, html

    def ids_name(self, ids):
        """ids_name(ids)
        Returns the ids string.
        """
        string, _ = self.get(ids)
        return string

    def ids_info(self, ids):
        """ids_name(ids)
        Returns the ids xml data.
        """
        _, html = self.get(ids)
        return html


#==============================================================================
#
#==============================================================================
class FrcFile(ResourceFile):
    def __init__(self, name, index):
        ResourceFile.__init__(self, name, index)
        self.strings = {}
        self.html = {}
        self.duplicates = []

        path = s_resources.get('frc_path', join(s_general['path'], 'EXE'))
        filename = "%s.frc" % join(path, self.name)
        if not exists(filename):
            raise ResourceError('Resource File Missing: %s' % filename)
        fih = open(filename, 'r')
        lines = []
        lines = fih.read()
        fih.close()
        lines = lines.splitlines()

        last_comments = []
        last_block = None
        for index, line in enumerate(lines):
            if not line:
                continue
            if COMMENT_RE.match(line):
                last_comments.append(line)
                continue

            match = BLOCK_RE.match(line)
            if not match and not last_block:
                log.error("%s (line: %s) - non-blank line before first block defined"
                          % (filename, index))
                continue
            elif not match:
                last_block.data.append(line)
                continue

            # new block
            ids = int(match.group(2))
            last_block = FrcBlock(match.group(1), ids, match.group(3))
            # add our comments and reset
            last_block.comments = last_comments
            last_comments = []
            if last_block.is_string():
                self.strings[ids] = last_block
            else:
                if self.strings.get(ids):
                    self.duplicates.append(ids)
                self.html[ids] = last_block

            if match.group(4):
                last_block.data.append("%s" % match.group(4))

    def get(self, ids): # pos not used for frc
        return self.strings.get(ids), self.html.get(ids)


    def ids_name(self, ids):
        string, _ = self.get(ids)
        return string and string.text() or None
        #if string is None:
        #    return
        #return string.text()


    def ids_info(self, ids):
        _, html = self.get(ids)
        return html and html.text() or None
        #if html is None:
        #    return
        #return html.text()


    def add(self, block, replace=False):
        if block.is_string():
            if self.html.has_key(block.ids):
                raise KeyError('Adding string %s but html exists' % block.ids)

            if self.strings.has_key(block.ids):
                if replace is False:
                    raise KeyError("string %s already exists" % block.ids)
                if not block.comments: # copy old comments
                    block.comments = self.strings[block.ids].comments

            self.strings[block.ids] = block
            return

        # add as html
        if self.strings.has_key(block.ids):
            raise KeyError('Adding html %s but string exists' % block.ids)

        if self.html.has_key(block.ids):
            if replace is False:
                raise KeyError("html %s already exists" % block.ids)
            if not block.comments: # copy old comments
                block.comments = self.html[block.ids].comments
        self.html[block.ids] = block

    def write(self):
        file_name = "%s.frc" % join(s_resources['frc_path'], self.name)
        fih = open(file_name, 'w')
        ids = self.strings.keys()
        ids.sort()
        if len(ids) > 0:
            prev = ids[0] - 1
        for i in ids:
            if i != 1 + prev: # numbers skipped, blank line spacer
                fih.write("\n")
            prev = i
            fih.write("%s\n" % self.strings[i])
        fih.write("\n\n")

        ids = self.html.keys()
        ids.sort()
        if len(ids) > 0:
            prev = ids[0] - 1
        for i in ids:
            #if id != 1 + prev:
            fih.write("\n")
            prev = i
            fih.write("%s\n" % self.html[i])
        fih.close()

#==============================================================================
#
#==============================================================================
class FrcBlock(object):
    data = None
    ids = None
    rtype = 'S'
    comments = None

    def __init__(self, rtype, ids, tag=None, data=None):
        if data is None:
            data = []
        self.data = data
        self.comments = []
        self.ids = ids
        self.rtype = rtype
        self.tag = tag

    def is_string(self):
        return self.rtype == 'S' and True or False
        #if self.rtype == 'S':
        #    return True
        #return False

    def is_xml(self):
        if self.rtype == 'S':
            return self.tag and True or False
            #if self.tag:
            #    return True
            #return False
        ## HTML string
        return not self.tag and True or False
        #if self.tag:
        #    return False
        #return True

    def text(self):
        data = self.data[:]
        data = [x.lstrip() for x in data]
        return '\n'.join(data)

    def build_string(self):
        info = "%s %s" % (self.rtype, self.ids)
        if self.tag:
            info = "%s %s" % (info, self.tag)
        if self.comments:
            info = "%s\n%s" % ('\n'.join(self.comments), info)

        data = self.data[:]
        if data[0][0] != '\t':
            data[0] = '\t%s' % data[0]
        if self.is_string() and not data[0] is None:
            info = "%s%s" % (info, data.pop(0))
        return '\n'.join([info] + data)

    def copy(self, ids=None):
        if ids is None:
            ids = self.ids
        new = FrcBlock(self.rtype, ids, self.tag)
        new.data = self.data[:]
        return new

    def __repr__(self):
        return self.build_string()

    def __str__(self):
        return self.build_string()


if __name__ == '__main__':
    # testing block
    pass