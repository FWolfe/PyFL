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
    freelancer.core

"""
from os.path import join, splitext
import freelancer.files.ini as ini
from freelancer.core.regex import LINE_SPLIT_RE
from . import settings
from . import data
from . import parser
from . import log
from . import resources
from . import hashes
config = None


def load_parser():
    log.info('Loading Rule Files')
    parser.load_rules(settings.general)

def load_resources():
    rset = settings.resources
    if rset is None: # no resource setting defined, skip loading
        # this probably should log a warning but some PyFL scripts
        # intentionally dont need resource access
        return
    resources.load(['resources.dll'] + config.find('resources')['dll'])


def load_config(queue_files=True):
    """loadConfig()
    Loads the Freelancer.ini, appends files listed in the [data] section to the
    queue of files to be loaded, and loads any resource dlls.
    Not required to be manually called when init() is used.
    """
    global config
    config = ini.IniFile(join(settings.general['path'], 'exe', 'freelancer.ini'))
    if queue_files is False:
        return
    dta = config.find('data')
    for line in dta.lines[1:]:
        try:
            match = LINE_SPLIT_RE.match(line)
            key, value, _ = match.groups() # _ is comments
        except AttributeError:
            continue
        data.queue_file(key, value)



def load_data_file(filename, group=None):
    """load_data_file(filename, group=None)
    Loads a single ini file, with the specified parser rule group.
    """
    try:
        return ini.IniFile(join('DATA', filename),
                           directory=settings.general['path'],
                           group=group,
                           flags=ini.FLAG_FLDATA + ini.FLAG_LOG + ini.FLAG_STAT)
    except ini.FileReadError:
        return None

def load_data_group(group):
    """load_data_group(group)
    Loads a specific data group defined in the freelancer.ini [data] section.
    """
    dta = config.find('data')
    grp = dta[group] # TODO: Temporarly Intentionally raise a KeyError
    if isinstance(grp, str):
        load_data_file(grp, group)
        return
    elif grp:
        for fil in grp:
            load_data_file(fil, group)

    try:
        for fil in settings.NONREFERENCED_FILES[group]:
            load_data_file(fil, group)
    except KeyError:
        pass


def load_queue():
    """loadQueue()
    Loads any files in the queue, not normally called externally.
    """
    files = data.file_queue
    while len(files) > 0:
        key, val = files.pop(0)
        if key == 'fonts_dir':
            # skip this, its in freelancer.ini, but points to a directory not file.
            continue
        load_data_file(val, key)


def load_nonreferenced():
    """loadNonReferenced()
    Loads non-referenced files. Specifically these files arent referenced in the
    Freelancer.ini, or any other files, but are required by the server.
    """
    #common.file_queue = [] # clear our queue
    for group, files in settings.NONREFERENCED_FILES.items():
        for filename in files:
            data.queue_file(group, filename)
    load_queue()



def validate_match_queue():
    """performMatchQueue()
    Does all queued cross reference validation checks (-m|--match rule arguments),
    comparing ini sections that link to other sections. Note unless everything
    (all files) were loaded, this wont work. Logs the errors.
    """
    import re
    import time
    log.log("Cross Reference Errors")
    start_time = time.time()
    _mre = re.compile('([^\:]+)?\:([^\:]+)?')
    count = 0
    for queue_index, queue_item in enumerate(data.match_queue):
        result = None
        obj, index, match, local, value = queue_item
        try:
            groups, sections = _mre.match(match.lower()).groups()
        except AttributeError:
            print queue_item
            exit()
        if not groups:
            groups = obj.file.group
        groups = groups.split('|')
        if sections:
            sections = sections.split('|')
        else:
            sections = (None,)

        if local: # ignore groups
            try:
                result = obj.file.keymap[value]
                if not result.section in sections:
                    result = None
            except KeyError:
                pass
        else:
            try:
                result = data.find_by_nickname(value, groups, sections)
            except KeyError as msg:
                log.error('keyerror: %s (%s)' % (msg, match))
                result = None

        if not result:
            count = 1 + count
            log.warn('FLData: %s doesnt match any %s from file %s (line %s)' %
                     (value, match, obj.file.path, obj.index + index))

    log.log("Cross Reference Results: %s items, %s errors, %s seconds" %
            (len(data.match_queue), count, time.time() - start_time))


def init(config_file='PyFL-Config.ini', minimal=False):
    """init()
    Initializes the PyFL engine, validates settings, loads and validates the parser
    rules, resets the errors.log, and loads the freelancer.ini file.
    """
    import time
    data._STATS[0] = time.time() # evil access of a private variable
    settings.load(config_file)
    # setup logging
    log.config(settings.general)
    log.log('------------------- PyFL Start -------------------')
    settings.validate()
    if minimal:
        return
    load_parser()
    load_config()
    load_resources()
    hashes.generate_cache()
