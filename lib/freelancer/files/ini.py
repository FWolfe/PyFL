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

r"""
    freelancer.files.ini - objects for dealing with freelancers data ini files.

    Due to the setup of Freelancer's .ini files, PyFL requires a libary as
    standard ones such as configparser wont do. Some features include:
    Write mode that preserves blank lines and ALL comments, template .ini files
    for data validation, and allowing multiple [Sections] of the same name and
    multiline 'key = value' pairs.


    Parser template files
    Templates define a template that defines what [Section] and 'key = value'
    lines are allowed, what keys can be included multiple times, and validates
    the value of each line. By default these are stored the etc\parser directory.


"""
from os.path import join, exists

from freelancer.core import log, parser
from freelancer.core import data as fldata
from freelancer.core.data import (stats_inc, STATS_LINES, STATS_FILES,
                                  STATS_SECTIONS, STATS_KEYS, STATS_ERRORS)
from freelancer.core.regex import SECTION_RE, LINE_COMMENT_RE, LINE_SPLIT_RE

s_general = None


FLAG_LOG = 1
FLAG_STAT = 2
FLAG_FLDATA = 4


def splitline(line):
    """splitline(line)
    Splits a string by commas and returns the list (or None). Note this uses a
    precompiled regex and does a better job then .split(',')
    """
    try:
        return LINE_SPLIT_RE.match(line).groups()
    except AttributeError:
        return None


def buildline(line):
    """buildline(line)
    returns a string representing a (key, value, comments) tuple.
    """
    try:
        if line[2] is None:
            return '%s = %s' % (line[0], line[1])
        return '%s = %s%s' % (line[0], line[1], line[2])
    except IndexError:
        return '%s = %s' % (line[0], line[1])


class FileReadError(Exception):
    """FileReadError
    """
    def __init__(self, message, path):
        log.error("File Read: %s --- %s" % (message, path))


class IniFile(list):
    r"""IniFile(filename, directory=None, group=None, flags=0))
    Reads and parses a ini file. a IniFile object acts as a list,
    and inherits all list methods. Each entry in the IniFile list is
    a IniSection object.
    filename = this can be a filename, or a full path and filename. This is
        often relative to the PyFL directory, OR Freelancer\Data directory
    directory = prepended to 'filename' when opening files. When dealing with
        FL data files this usually points to the Freelancer\Data directory
    group = a parser rule group to use when parsing.
    flags = bitwise combo of FLAG_LOG, FLAG_STAT, FLAG_FLDATA

    IniFile objects function as lists, so ini [Sections] can be accessed by
    index, iterated through, or resorted.

    # get all [Zone] sections from New York system
    zones = [z for z in systems.get_system('li01') if z.section == 'zone']

    Each [Section] in the ini file is created as a IniSection object.
    """
    fullpath = None # full path (or relative to our working PyFL directory)
    changed = False # True if file has changed and needs update()
    group = None # file type group...goods equipmemnt, etc
    keymap = None
    path = None

    _head = None # top lines above [any sections]
    _data = None # list of all raw unparsed lines in file

    def __init__(self, filename, directory=None, group=None, flags=0):
        list.__init__(self)
        self.flags = flags

        if flags&FLAG_FLDATA:
            # FL data ini, check if its loaded, and specify we're loading it
            if fldata.is_loaded(filename):
                return None
            fldata.add_file(filename, self)

        if flags&FLAG_LOG:
            log.info('Reading File (%s): %s' % (group, filename))

        if directory:
            self.fullpath = join(directory, filename)
        else:
            self.fullpath = filename
        if group:
            group = group.lower()
        self.group = group
        self.path = filename
        self.keymap = {} # this is only matters if its a data file
        self._head = []

        if flags&FLAG_STAT:
            stats_inc(STATS_FILES)

        self.read()


    def read(self):
        """IniFile.read()
        Reads and parses the ini file into IniSections
        """
        # read file
        if not exists(self.fullpath):
            raise FileReadError("Missing File", self.path)

        fih = open(self.fullpath)
        lines = fih.read()
        fih.close()
        if lines[0:4] == 'BINI':
            raise FileReadError("BINI File file detected, refusing to read." +
                                " This may generate additional warnings later",
                                self.fullpath)
        lines = lines.splitlines()


        last = [] # lines of the last section
        section = None
        index = 0

        _data = []
        for i, line in enumerate(lines):
            line = line.rstrip()
            if self.flags&FLAG_STAT:
                stats_inc(STATS_LINES)

            match = SECTION_RE.match(line) # check for new [section]
            if match and not section is None:
                # found first section in the file
                _data.append((section, last, index))

            if match:
                # set tracking variables
                index = 1 + i
                section = match.group(1).lower()
                last = [line]
                continue

            if section is None:
                # got lines but no section, probably file header comments
                self._head.append(line)
            else:
                last.append(line)

        if section: # append last section in file
            _data.append((section, last, index))

        for section, lines, index in _data:
            self.append(IniSection(section, lines, index, self))


    def find(self, section, index=0):
        """IniFile.find(section)
        Finds and returns the first IniSection() object of the specified type.
        """
        section = section.lower()
        results = [x for x in self if x.section == section]
        if index is None:
            return results
        try:
            return results[index]
        except IndexError:
            return None


    def findall(self, section):
        """IniFile.findall(section)
        Returns a list of IniSection() objects all that match the specified
        [section]. This is a wrapper for .find(setion, index=None)
        """
        return self.find(section, index=None)


    def resort(self, sort_list, cmp_func):
        """IniFile.resort(self, sort_list, cmp_func)
        Resorts the IniSection() objects based on the order specified in
        sort_list. basically it does (sort of):

        for item in sort_list:
            for obj in self:
                if cmp_func(item, obj) is True:
                    new_order.append(obj)
        new_order.append(leftovers)

        Unsorted sections are appended to the bottom.
        Note IniFile.update() must be called to save the changes.

        example: resort based on a list of section names
        .resort(section_list, lambda item, obj: obj.section == item)

        example: resort based on list of nicknames
        .resort(name_list, lambda item, obj: obj.get('nickname','').lower() == item)
        """
        done = []
        for sort_item in sort_list:
            popped = []
            for index, section in enumerate(self):
                if not cmp_func(sort_item, section):
                    continue
                popped.append(index)
                done.append(section)

            count = 0
            for index in popped:
                self.pop(index-count)
                count += 1
        self[0:] = done + self
        self.changed = True


#==============================================================================
#
#     def resortBySectionKey(self, section, key, sort_list):
#         """IniFile.resortBySectionKey(key, section, key, sort_list)
#         Resorts the IniSection() objects based on the given key, but only for the
#         specified section, keeping order of trailing sections. Ideal for sorting
#         things like mbases.ini where trailing sections matter.
#         """
#         done = []
#         keep = False
#         for sort_item in sort_list:
#             popped = []
#             for index, current_section in enumerate(self):
#
#                 if current_section.section == section: # right type
#                     keep = False
#                 elif keep: # keep is true, so keep order here
#                     popped.append(index)
#                     done.append(current_section)
#                     continue
#                 else:
#                     continue
#
#                 val = current_section.get(key)
#                 if not val or val.lower() != sort_item.lower():
#                     continue
#                 keep = True # everything matches, set keep
#
#                 popped.append(index)
#                 done.append(current_section)
#
#             count = 0
#             for index in popped:
#                 self.pop(index-count)
#                 count += 1
#         self[0:] = done + self
#         self.changed = True
#
#==============================================================================


    def backup(self):
        """IniFile.backup()
        Creates a backup of the original file with the .bak extension.
        """
        import shutil
        shutil.copy2(self.fullpath, "%s.bak" % self.fullpath)


    def write(self, backup=True):
        """IniFile.write(backup=True)
        Writes the data in memory to the file, optionally creating a backup first.
        """
        if backup:
            self.backup()

        fih = open(self.fullpath, 'w')
        if self._head:
            fih.write("%s\n" % '\n'.join(self._head))
        for obj in self:
            string = '\n'.join(obj.lines)
            end = '\n'
            if string[-2:] == '\n\n':
                end = ''
            fih.write("%s%s" % (string, end))
        fih.close()


    def update(self, backup=True):
        """IniFile.update(backup=True)
        Writes the data in memory to the file if it has changed, optionally creating
        a backup first.
        """
        if not self.changed:
            return False
        self.write(backup)
        self.changed = False
        for obj in self:
            obj.changed = False


    def __repr__(self):
        return "%s (%s sections)" % (self.path, len(self))


    def __cmp__(self, other):
        if isinstance(other, str):
            return other == self.fullpath
        assert isinstance(other, IniFile)
        return other.fullpath == self.fullpath


    def __hash__(self):
        return id(self)



#==============================================================================
#
#==============================================================================

class IniSection(dict):
    """IniSection(self, section, lines=None, index=None, parent=None)
    Object representing a [Section] in a ini file. It is not required to manually
    create these in your code, they are automatically generated when parsing a ini
    file.

    IniSection objects function as dicts:
    zone_names = [z['nickname'] for z in zones]

    """
    section = None # name of section
    lines = None # raw data
    index = None # line index for start of section in ini
    file = None # ini file
    changed = False # content has changed
    keyorder = None
    rules = None
    group = None

    def __init__(self, section, lines=None, index=None, parent=None):
        dict.__init__(self)

        if lines is None:
            lines = []
        self.section = section
        self.lines = lines
        self.index = index
        self.file = parent
        self.group = parent.group
        self.keyorder = []

        self._stat(STATS_SECTIONS) # increment stats
        self.parse()

    def parse(self):
        """IniSection.parse()
        Parses the data for the section. This is normally automatically called
        when the section is generated (ie: the file has been read)
        """
        rules = None
        required = []

        # check if this file has a group. if so we need to fetch the parsing rules
        if self.group:
            try:
                rules = parser.get_rules(self.group, self.section)
                required = rules.required
            except KeyError:
                self._stat(STATS_ERRORS) # increment stats
                self._warn("FLData: (%s:%s) Unknown section in file %s (line %s)" %
                           (self.group, self.section, self.file.path, self.index))
        self.rules = rules
        # parse each line
        for i, line in enumerate(self.lines[1:]):
            i = 1+ i
            if not LINE_COMMENT_RE.sub('', line):
                continue # blank line

            match = LINE_SPLIT_RE.match(line)
            if not match:
                self._stat(STATS_ERRORS) # increment stats
                self._warn("FLData: Bad line in file %s (line %s)" %
                           (self.file.path, i + self.index))
                continue

            key = match.group(1).lower()
            val = match.group(2)
            self.keyorder.append(key)
            self._stat(STATS_KEYS) # increment stats
            self._setkey(i, key, val)

        # check for a sortkey 'ie: nickname ='
        if rules and rules.sortkey:
            self._add_unique_key()

        if not required:
            return

        # check required keys exist
        for req in required:
            if self.get(req, None) is None:
                self._stat(STATS_ERRORS) # increment stats
                self._warn("FLData: (%s:%s) Missing Required key '%s' in file %s (line %s)" %
                           (self.group, self.section, req, self.file.path, self.index))


    def get(self, key, default=None, dtype=None):
        """IniSection.get(self, key, default=None, dtype=None)
        Returns a value from the ini section for the given key. If default is
        specified returns that value if the key is not found. If dtype is
        specified the returned value is converted to that data type (str, float,
        int etc). dtype can also be a function that takes a single argument and
        returns a value.

        zone_pos = [z.get('pos', dtype=positions.Pos) for z in zones]

        ship.get('ids_name') or ship['ids_name'] both return string versions
        ship.get('ids_name', default=0, dtype=int) will return a int value.

        When bool is passed as the dtype, the strings 'ON, YES, TRUE, 1' all return
        True, and 'OFF, NO, FALSE, 0' will return False:

        # only returns False if bool_key is not set. If set to 'False' this will
        # still return True
        bool(section.get('bool_key', default=False))

        # returns a proper True/False
        section.get('bool_key', default=False, dtype=bool)
        """
        value = dict.get(self, key, default)
        if dtype is bool:
            if value.upper() in ('TRUE', '1', 'YES', 'ON'):
                value = True
            elif value.upper() in ('FALSE', '0', 'NO', 'OFF'):
                value = False
        try:
            return dtype(value)
        except TypeError:
            return value
        except ValueError:
            return value


    def set(self, key, value):
        """IniSection.set(self, key, value)
        """
        self[key] = value
        self.changed = True
        self.file.changed = True

        self.edit_key(key, value)

    def edit_key(self, key, value):
        """IniSection.edit_key(self, key, value)
        """
        items = []
        for i, line in enumerate(self.lines):
            split = splitline(line)
            if split and split[0].lower() == key:
                items.append((i, list(split)))

        if isinstance(value, (str, int, float)):
            value = [value]

        if len(items) != len(value):
            raise NotImplementedError

        for index, val in enumerate(value):
            line_index, line = items[index]
            line[1] = val
            self.lines[line_index] = buildline(line)


    def _setkey(self, index, key, value):
        """IniSection._setkey(index, key, value)
        Internal Function. This sets the key in the IniSection dict to the
        value, and validates the value with the rules.
        """
        # no rules to follow, just do it
        if self.rules is None:
            if not self.get(key, None):
                self[key] = value
            elif isinstance(self[key], list):
                self[key].append(value)
            else:
                self[key] = [self[key], value]
            return

        # find the rule for this key
        rule = self.rules.get(key.lower())
        if rule is None:
            stats_inc(STATS_ERRORS) # increment stats
            log.warn("FLData: (%s:%s) Unknown key '%s = %s' in file %s (line %s)" %
                     (self.group, self.section, key, value, self.file.path, self.index + index))
            return

        elif self.has_key(key) and not rule.multiline:
            stats_inc(STATS_ERRORS) # increment stats
            log.warn("FLData: (%s:%s) Key '%s' is not multiline in file %s (line %s)" %
                     (self.group, self.section, key, self.file.path, self.index + index))
            return

        if s_general.get('validate_data', dtype=bool):
            match_check = s_general.get('match_checks', dtype=bool)
            rule.check(self, index, key, value, match_check=match_check)

        if rule.multiline:
            self[key] = self.get(key, [])
            self[key].append(value)
        else:
            self[key] = value


    def _add_unique_key(self):
        """IniSection._add_unique_key()
        Internal function. Adds the key to the core.data handlers.
        """
        key = self.rules.sortkey
        key = key.lower()
        try:
            value = self[key]
        except KeyError:
            self._stat(STATS_ERRORS) # increment stats
            self._warn("FLData: (%s:%s) Missing required sort key '%s' in file %s (line %s)" %
                       (self.group, self.section, key, self.file.path, self.index))
            return
        from freelancer.core.parser import GLOBAL_UNIQUE, GROUP_UNIQUE, SECTION_UNIQUE, \
                LOCAL_UNIQUE

        value = value.lower()
        sortrule = self.rules[key]
        sorttype = sortrule.sortkey

        # GLOBAL UNIQUE CHECK
        if sorttype == GLOBAL_UNIQUE:
            try:
                fldata.add_unique_global_key(value, self)
            except fldata.FLSectionError:
                pass # already handled

        # GROUP UNIQUE CHECK
        if GLOBAL_UNIQUE + GROUP_UNIQUE & sorttype:
            try:
                fldata.add_unique_group_key(value, self)
            except fldata.FLGroupError:
                pass # already handled

        if GLOBAL_UNIQUE + GROUP_UNIQUE + SECTION_UNIQUE & sorttype:
            try:
                fldata.add_unique_section_key(value, self)
            except fldata.FLSectionError:
                pass # already handled

        elif sorttype == LOCAL_UNIQUE:
            keymap = self.file.keymap
            if keymap.get(value):
                self._stat(STATS_ERRORS) # increment stats
                self._warn("FLData: Duplicate Local Unique '%s' in file %s (line %s)" %
                           (value, self.file.path, self.index))
            else:
                keymap[value] = self
        else:
            log.critical("Invalid sortype (%s), bug in parsing engine..." % sorttype)
            assert False


    def _stat(self, index, value=1):
        if self.file.flags&FLAG_STAT:
            stats_inc(index, value)


    def _warn(self, message):
        if self.file.flags&FLAG_LOG:
            log.warn(message)


    def __repr__(self):
        return '%s' % self.section

