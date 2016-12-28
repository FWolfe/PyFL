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
    freelancer.core.data
"""

import os
#import freelancer.exceptions as flex
from freelancer.core import log

# all loaded Ini files
_LOADED = {} # _LOADED[file path] = IniFile()
# queue of files to load
file_queue = [] # file_queue[index] = (group, path)
# queue of nicknames to match
match_queue = []
# files
files = {}

# all of fl's data
_DATA = {} # _DATA[group][section][sortkey] = DataSection()


# referenced files
_REFERENCED = {} # _REFERENCED[path] = int
_UNIQUE = {}
_GROUP_UNIQUE = {}

# Stats handling
_STATS = [0, 0, 0, 0, 0, 0, 0] # [time, files parsed, lines parsed, sections, keys, args, errors]
STATS_TIME = 0
STATS_FILES = 1
STATS_LINES = 2
STATS_SECTIONS = 3
STATS_KEYS = 4
STATS_ARGS = 5
STATS_ERRORS = 6

#==============================================================================
#
#==============================================================================
class FLDataError(Exception):
    def __init__(self, message):
        log.error(message)


class FLGroupError(FLDataError):
    def __init__(self, message, group):
        FLDataError.__init__(self, 'FLData (%s): %s' % (group, message))


class FLSectionError(FLDataError):
    def __init__(self, message, group, section):
        FLDataError.__init__(self, 'FLData (%s:%s): %s' % (group, section, message))


class FLKeyError(FLDataError):
    def __init__(self, message, group, section):
        FLDataError.__init__(self, 'FLData (%s:%s): %s' % (group, section, message))


def get_group(group, create=False):
    """get_group(group)
    Returns a dict of DataSection() groups, where keys are the section names,
    and values are dict objects.
    """
    group = group.lower()
    if create is True:
        _DATA[group] = _DATA.get(group, {})
    try:
        return _DATA[group]
    except KeyError:
        raise FLGroupError("No such group in data", group)


def get_sections(group, section, create=True):
    """get_sections(group, section)
    Returns a dict of DataSections() from the specified group, where keys are the
    sortkeys (defined in the parser rule files) and values are DataSection() objects.
    """
    section = section.lower()
    if create is True:
        grp = get_group(group, True)
        grp[section] = grp.get(section, {})

    try:
        return get_group(group)[section]
    except KeyError:
        raise FLSectionError("No such section in data", group, section)

def get_key(group, section, key):
    """get_key(group, section, key)
    """
    key = key.lower()
    try:
        return get_sections(group, section)[key]
    except KeyError:
        raise FLKeyError("Invalid key %s" % key, group, section)

def get_group_files(group):
    """get_group_files(group)
    Returns a list of all DataFiles() for the specified group.
    """
    return [x for x in _LOADED.values() if x.group == group]


def find_by_nickname(sortkey, groups=None, sections=None):
    """findByNickname(name, groups=None, subgroups=None)
    Returns a list of DataSection() objects that match the given nickname.
    If groups or subgroups are specified list is filtered by those types.
    """
    results = []
    sortkey = sortkey.lower()
    if groups is None or groups == (None,):
        groups = _DATA.keys()

    for group in groups:
        group_dict = _DATA[group]
        new_sections = sections
        if new_sections is None or new_sections == (None,):
            new_sections = group_dict.keys()

        for section in new_sections:
            try:
                results.append(group_dict[section][sortkey])
            except KeyError:
                continue

    return results

#==============================================================================
#
#==============================================================================

def is_loaded(path):
    if _LOADED.has_key(path.lower()):
        return True
    return False


def add_file(path, data):
    _LOADED[path.lower()] = data


def get_file(path):
    """get_file(path)
    Returns the DataFile() or IniFile() object for the given path.
    For example to get the freelancer.ini would be get_file(r'exe\freelaner.ini')
    """
    return _LOADED[path.lower()]


def get_data_file(path):
    r"""get_data_file(path)
    Returns the DataFile() or IniFile() object for the given path in the data folder.
    For example to get the shiparch.ini would be get_data_file(r'ships\shiparch.ini')
    """
    path = os.path.join('data', path).lower()
    return _LOADED[path]

#==============================================================================
#
#==============================================================================
def queue_match(data):
    match_queue.append(data)

def queue_file(group, path):
    if (group, path) in file_queue:
        return
    log.debug("File Queue: Appending (group: %s, path: %s)" % (group, path))
    file_queue.append((group, path))

def dequeue_file():
    return file_queue.pop(0)


def add_reference(path):
    _REFERENCED[path] = 1 + _REFERENCED.get(path, 0)


def add_unique_global_key(key, value):
    if _UNIQUE.has_key(key):
        stats_inc(STATS_ERRORS)
        raise FLSectionError("Duplicate global unique '%s' in file %s (line %s)" %
                             (key, value.parent.path, value.index), value.group, value.section)
    _UNIQUE[key] = value

def add_unique_group_key(key, value):
    _GROUP_UNIQUE[value.group] = _GROUP_UNIQUE.get(value.group, {})
    gu = _GROUP_UNIQUE[value.group]
    if gu.has_key(key):
        stats_inc(STATS_ERRORS)
        raise FLGroupError("Duplicate group unique '%s' in file %s (line %s)" %
                           (key, value.parent.path, value.index), value.group)
    gu[key] = value

def add_unique_section_key(key, value):
    _DATA[value.group] = _DATA.get(value.group, {})
    data = _DATA[value.group]
    data[value.section] = data.get(value.section, {})
    data = data[value.section]
    if data.get(key):
        stats_inc(STATS_ERRORS)
        raise FLSectionError("Duplicate group:section unique '%s' in file %s (line %s)" %
                             (key, value.parent.path, value.index), value.group, value.section)
    data[key] = value


#==============================================================================
#
#==============================================================================
def stats_inc(stat, value=1):
    _STATS[stat] += value



#==============================================================================
#
#==============================================================================

