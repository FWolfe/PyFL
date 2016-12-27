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
    freelancer.files.ini - objects for dealing with freelancers ini and
    data files.

"""
# pylint: disable=C0301
# pylint: disable=C0103

import re
from os.path import join, exists

#from freelancer.bin import flHash
from freelancer.core import log, parser
from freelancer.core import data as fldata
from freelancer.core.data import stats_inc, STATS_LINES, STATS_FILES, STATS_SECTIONS, STATS_KEYS, STATS_ERRORS
from freelancer.core.regex import LINE_TRIM_RE, SECTION_RE, LINE_COMMENT_RE, LINE_SPLIT_RE

s_general = None


class FileReadError(Exception):
    """FileReadError

    """

class IniFile(list):
    """IniFile(path)
    Reads and parses a ini file. a IniFile object acts as a list,
    and inherits all list methods. Each entry in the IniFile list is
    a IniSection object.
    """
    fullpath = None
    _head = None # top lines above [any sections]
    changed = False # True if file has changed and needs update()

    def __init__(self, path):
        if not exists(path):
            log.warn("Missing File: %s" % path)
            raise FileReadError
        list.__init__(self)
        self.fullpath = path
        self._head = []

        # read file
        fi = open(path)
        lines = fi.read()
        fi.close()
        if lines[0][0:4] == 'BINI':
            log.warn("Ignoring file: %s\n\tBINI file detected, refusing to read. This may generate additional warnings later" % path)
            raise FileReadError
        self.raw = re.split('\n', lines)
        self._parse()

    def _parse(self):
        """IniFile._parse()
        Internal function, breaks the file into IniSection() objects, called after
        reading the IniFile.
        """
        last = []
        section = None
        index = 0

        for i, line in enumerate(self.raw):
            line = LINE_TRIM_RE.sub('', line)
            match = SECTION_RE.match(line) # check for new [section]
            if match and not section is None:
                self.append(IniSection(section, raw=last, index=index, parent=self))

            if match:
                index = 1 + i
                section = match.group(1)
                last = [line]
                continue

            if section is None:
                self._head.append(line)
            else:
                last.append(line)

        if section: # create last section
            self.append(IniSection(section, raw=last, index=index, parent=self))
        self.raw = None # clear raw data, its stored in our IniSections

    def find(self, section):
        """IniFile.find(section)
        Finds and returns the first IniSection() object of the specified type.
        """
        for x in self:
            if x.section == section:
                return x

    def findSections(self, section):
        """IniFile.findSections(section)
        Returns a list of IniSection() objects all that match the specified type.
        """
        section = section.lower()
        return [x for x in self if x.section == section]

    def resortBySections(self, section_list):
        """IniFile.resortBySections(section_list)
        Resorts the IniSection() objects based on the order specified in section_list.
        Unsorted sections are appended to the bottom.
        Note IniFile.update() must be called to save the changes.
        """
        done = []
        for section_type in section_list:
            popped = []
            for index, section in enumerate(self):
                if section.section != section_type:
                    continue
                popped.append(index)
                done.append(section)

            count = 0
            for p in popped:
                self.pop(p-count)
                count += 1
        self[0:] = done + self
        self.changed = True


    def resortByKeys(self, key, sort_list):
        """IniFile.resortByKeys(key, sort_list)
        Resorts the IniSection() objects based on the given key in the order
        specified in sort_list. Unsorted sections are appended to the bottom.
        Note IniFile.update() must be called to save the changes.
        """
        done = []
        for sort_item in sort_list:
            popped = []
            for index, section in enumerate(self):
                val = section.get(key)
                if not val or val.lower() != sort_item.lower():
                    continue
                popped.append(index)
                done.append(section)

            count = 0
            for p in popped:
                self.pop(p-count)
                count += 1
        self[0:] = done + self
        self.changed = True


    def resortBySectionKey(self, section, key, sort_list):
        """IniFile.resortBySectionKey(key, section, key, sort_list)
        Resorts the IniSection() objects based on the given key, but only for the
        specified section, keeping order of trailing sections. Ideal for sorting
        things like mbases.ini where trailing sections matter.
        """
        done = []
        keep = False
        for sort_item in sort_list:
            popped = []
            for index, current_section in enumerate(self):
                if current_section.section == section: # right type
                    keep = False
                elif keep: # keep is true, so keep order here
                    popped.append(index)
                    done.append(current_section)
                    continue
                else:
                    continue

                val = current_section.get(key)
                if not val or val.lower() != sort_item.lower():
                    continue
                keep = True # everything matches, set keep
                popped.append(index)
                done.append(current_section)

            count = 0
            for p in popped:
                self.pop(p-count)
                count += 1
        self[0:] = done + self
        self.changed = True


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
        for s in self:
            st = '\n'.join(s.raw)
            e = '\n'
            if st[-2:] == '\n\n':
                e = ''
            fih.write("%s%s" % (st, e))
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
        for s in self:
            s.changed = False

    def __repr__(self):
        return "%s (%s sections)" % (self.fullpath, len(self))


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
    """IniSection(object)
    Object representing a [section] in a ini file. It is not required to manually
    create these in your code, they are automatically generated when parsing a ini
    file.
    """
    section = None # name of section
    raw = None # raw data
    index = None # start position in ini
    parent = None # ini file
    changed = False # content has changed
    keyorder = None

    def __init__(self, section, raw=None, index=None, parent=None):
        dict.__init__(self)
        if raw is None:
            raw = []
        self.section = section.lower()
        self.raw = raw
        self.index = index
        self.parent = parent
        self.keyorder = []

        self._parse()

    def _parse(self):

        for i, line in enumerate(self.raw[1:]):
            i = 1+ i
            if not LINE_COMMENT_RE.sub('', line):
                continue

            m = LINE_SPLIT_RE.match(line)
            if not m:
                continue
            key = m.group(1).lower()
            val = m.group(2)
            self.keyorder.append(key)
            self._setkey(key, val)


    def _setkey(self, key, val):
        if not self.get(key, None):
            self[key] = val
        elif isinstance(self[key], list):
            self[key].append(val)
        else:
            self[key] = [self[key], val]

    def get(self, key, default=None, dtype=None):
        """get(self, key, default=None, dtype=None)
        Returns a value from the ini section for the given key. If default is
        specified returns that value if the key is not found. If dtype is
        specified the returned value is converted to that data type (str, float,
        int etc). dtype can also be a function that takes a single argument and
        returns a value.
        """
        value = dict.get(self, key, default)
        if dtype is bool:
            if value.upper() in ('TRUE','1', 'YES'):
                value = True
            elif value.upper() in ('FALSE', '0', 'NO'):
                value = False
        try:
            return dtype(value)
        except TypeError:
            return value
        except ValueError:
            return value

    def set(self, key, value):
        """set(self, key, value)

        """
        def buildline(li):
            try:
                if li[2] is None:
                    return '%s = %s' % (li[0], li[1])
                return '%s = %s %s' % (li[0], li[1], li[2])
            except IndexError:
                return '%s = %s' % (li[0], li[1])


        self[key] = value
        self.changed = True
        self.parent.changed = True

        k = self.findKeys(key)
        if isinstance(value, (str, int, float)):
            value = [value]

        if len(k) != len(value):
            raise NotImplementedError

        for i, v in enumerate(value):
            ck = k[i]
            ck[1][1] = v
            self.raw[ck[0]] = buildline(ck[1])


    def findKeys(self, key):
        result = []
        for i, line in enumerate(self.raw):
            s = splitLine(line)
            if s and s[0].lower() == key:
                result.append((i, list(s)))
        return result

    def __repr__(self):
        return '%s' % self.section


#==============================================================================
#
#==============================================================================

class DataIniFile(IniFile):
    group = None # file type group...goods equipmemnt, etc
    local_uniques = None
    path = None
    def __init__(self, path, directory, group):
        """group = The rule parser group to use. Defaults to None.
            If not set, no rules will be used
        """

        # already loaded
        if fldata.is_loaded(path):
            return None
        log.info('Reading File (%s): %s' % (group, path))

        fullpath = join(directory, path)

        self.path = path
        if group:
            group = group.lower()
        self.group = group

        stats_inc(STATS_FILES)
        fldata.add_file(path, self)
        # parser
        self.local_uniques = {}

        IniFile.__init__(self, fullpath)

    def _parse(self):
        last = []
        section = None
        index = 0
        for i, l in enumerate(self.raw):
            l = LINE_TRIM_RE.sub('', l)
            stats_inc(STATS_LINES)
            #stats[2] += 1
            m = SECTION_RE.match(l)
            if m and not section is None:
                self.append(DataSection(section, raw=last, index=index, parent=self))
            if m:
                index = i+1
                section = m.group(1)
                last = [l]
                continue

            if section is None:
                self._head.append(l)
            else:
                last.append(l)

        if section:
            self.append(DataSection(section, raw=last, index=index, parent=self))

        self.raw = None

#==============================================================================
#
#==============================================================================

class DataSection(IniSection):
    sortkey = None
    def __init__(self, section, raw=None, index=None, parent=None):
        stats_inc(STATS_SECTIONS)
        #stats[3] += 1 # increment # of sections
        self.group = parent.group
        IniSection.__init__(self, section, raw, index, parent)

    def _parse(self):
        #group = self.parent.group
        rules = None
        required = []
        try:
            rules = parser.get_rules(self.group, self.section)
            required = rules.required
        except KeyError:
            stats_inc(STATS_ERRORS)
            log.warn("FLData: (%s:%s) Unknown section in file %s (line %s)" %
                     (self.group, self.section, self.parent.path, self.index))

        for i, line in enumerate(self.raw[1:]):
            i = 1 + i
            if not LINE_COMMENT_RE.sub('', line):
                continue

            m = LINE_SPLIT_RE.match(line)
            if not m:
                stats_inc(STATS_ERRORS)
                log.warn("FLData: Bad line in file %s (line %s)" %
                         (self.parent.path, i + self.index))
                continue

            key = m.group(1).lower()
            val = m.group(2)
            self.keyorder.append(key)

            stats_inc(STATS_KEYS)
            #############################################

            if rules:
                self._setkey(i, rules, key, val)
            else:
                IniSection._setkey(self, key, val)


        # check required keys exist
        for req in required:
            if self.get(req, None) is None:
                stats_inc(STATS_ERRORS)
                log.warn("FLData: (%s:%s) Missing Required key '%s' in file %s (line %s)" %
                         (self.group, self.section, req, self.parent.path, self.index))
        if rules and rules.sortkey:
            self._addSortkey(rules)


    def _setkey(self, index, rules, key, value):
        rule = rules.get(key.lower())
        if rule is None:
            stats_inc(STATS_ERRORS)
            log.warn("FLData: (%s:%s) Unknown key '%s = %s' in file %s (line %s)" %
                     (self.group, self.section, key, value, self.parent.path, self.index + index))
            return

        elif self.has_key(key) and not rule.multiline:
            stats_inc(STATS_ERRORS)
            log.warn("FLData: (%s:%s) Key '%s' is not multiline in file %s (line %s)" %
                     (self.group, self.section, key, self.parent.path, self.index + index))
            return

        # TODO: fix validation
        if s_general.get('validate_data', 'TRUE').upper() == 'TRUE':
            match_check = s_general.get('match_checks', 'FALSE').upper() == 'TRUE' and True or False
            
            rule.check(self, index, key, value, match_check=match_check)

        if rule.multiline:
            self[key] = self.get(key, [])
            self[key].append(value)
        else:
            self[key] = value


    def _addSortkey(self, rules):
        sortkey = rules.sortkey
        try:
            sortval = self[sortkey]
        except KeyError:
            stats_inc(STATS_ERRORS)
            log.warn("FLData: (%s:%s) Missing required sort key '%s' in file %s (line %s)" %
                     (self.group, self.section, sortkey, self.parent.path, self.index))
            return
        from freelancer.core.parser import GLOBAL_UNIQUE, GROUP_UNIQUE, SECTION_UNIQUE, \
                LOCAL_UNIQUE, HASH_UNIQUE

        #flHash(sortval)
        sortval = sortval.lower()
        sortrule = rules[sortkey.lower()]
        sorttype = sortrule.sortkey

        # GLOBAL UNIQUE CHECK
        if sorttype == GLOBAL_UNIQUE:
            try:
                fldata.add_unique_global_key(sortval, self)
            except fldata.FLSectionError:
                pass # already handled

        # GROUP UNIQUE CHECK
        if GLOBAL_UNIQUE + GROUP_UNIQUE & sorttype:
            try:
                fldata.add_unique_group_key(sortval, self)
            except fldata.FLGroupError:
                pass # already handled

        if GLOBAL_UNIQUE + GROUP_UNIQUE + SECTION_UNIQUE & sorttype:
            try:
                fldata.add_unique_section_key(sortval, self)
            except fldata.FLSectionError:
                pass # already handled

        elif sorttype == LOCAL_UNIQUE:
            lu = self.parent.local_uniques
            if lu.get(sortval):
                stats_inc(STATS_ERRORS)
                log.warn("FLData: Duplicate Local Unique '%s' in file %s (line %s)" %
                         (sortval, self.parent.path, self.index))
            else:
                lu[sortval] = self

        elif sorttype == HASH_UNIQUE:
            pass
        else:
            log.error("this should never be seen...bug?")
            log.debug(self.parent.path.replace('\\', '/'))
            log.debug("%s %s %s %s %s)" % (self.index, self.parent.group, sortkey, sortval, sorttype))
            assert False



#==============================================================================
#
#
#    bool    - true, false, 1 or 0
#    byte    - 0 to 255
#    int     - pos/neg number without decimals
#    float   - pos/neg number including decimals
#    ids     - a dll resource entry
#    arch    - a FL hash code, signed, unsigned or hex
#    word    - string with no spaces
#    file    - a file we check exists
#    ini     - a .ini file we load and parse
#    cmp     - a .cmp or .3db file
#    mat     - a .mat file
#    wav     - a .wav file
#    ale     - a .ale effect file
#    thn     - a .thn script
#    string  - any other value that can include any ammount of any character
#            like spaces (but not ,)
#
#==============================================================================

def splitLine(line):
    m = LINE_SPLIT_RE.match(line)
    if m:
        return m.groups()
    return None


