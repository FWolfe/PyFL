# -*- coding: utf-8 -*-
"""
Created on Sat Dec 24 16:34:29 2016

@author: Fenris_Wolf
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
    for line in dta.raw[1:]:
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
        return ini.DataIniFile(join('DATA', filename), settings.general['path'], group)
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
        ini, index, match, local, value = queue_item
        try:
            groups, sections = _mre.match(match.lower()).groups()
        except AttributeError:
            print queue_item
            exit()
        if not groups:
            groups = ini.parent.group
        groups = groups.split('|')
        if sections:
            sections = sections.split('|')
        else:
            sections = (None,)

        if local: # ignore groups
            try:
                result = ini.parent.local_uniques[value]
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
            log.warn('FLData: %s doesnt match any %s from file %s (line %s)' % (value, match, ini.parent.path, ini.index + index))

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
