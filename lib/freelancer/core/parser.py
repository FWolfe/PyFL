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
    freelancer.core.parser - Module for dealing with parser rules, and validating the
    data in freelancer's ini files. Most of this file will not need to be called in
    your code, as its almost entirely part of the PyFL core.
"""

import re
import os
from os.path import join, exists
from collections import namedtuple
from freelancer.core import log
from freelancer.core.data import add_reference, queue_match, queue_file, stats_inc, STATS_ARGS
from freelancer.core.regex import *

# Parsing rules
_RULES = {} # _RULES[group][section] = SectionRules()
_VALIDFLAGS = ( # valid flags that can be defined in rule file lines
    'req', 'multi', 'uglobal', 'ugroup', 'usection', 'ulocal', 'uhash', 'local', 'none'
)

GLOBAL_UNIQUE = 1
GROUP_UNIQUE = 2
SECTION_UNIQUE = 4
LOCAL_UNIQUE = 8
HASH_UNIQUE = 16


RuleArg = namedtuple('RuleArg', ('type', 'count', 'options'))
s_general = None # set in freelancer.core.init()

#==============================================================================
#
#==============================================================================
class RuleFileError(Exception):
    def __init__(self, message, group='', section='', key=''):
        log.critical("Parser: (%s:%s:%s) %s" % (group, section, key, message))
        exit()

#==============================================================================
#
#==============================================================================

class SectionRules(dict):
    """SectionRules(group, section, lines)
    A object representing parser rules for a ini [section]. Your code will never need
    to manually create these, they are generated automatically when reading the parser
    rule files. Errors in the files will generate a RuleFileError exception here, which
    should never be handled by your code unless its for customizing the message.
    If the rules have errors, its best not to continue running.
    """
    group = None
    section = None
    sortkey = None # the type of sortkey used. bitwise flags
    required = None

    def __init__(self, group, section, lines):
        if _RULES[group].has_key(section):
            raise RuleFileError('[%s] defined twice!' % section, group, section)

        dict.__init__(self)
        _RULES[group][section] = self
        self.group = group
        self.section = section

        for line in lines:
            line = LINE_COMMENT_RE.sub('', line) # remove comments
            if not line: # blank
                continue
            match = LINE_SPLIT_RE.match(line)
            if not match: # bad line?
                raise RuleFileError("Bad line: %s" % line, group, section)
            key, value, _ = match.groups() #  _ is comments
            self[key.lower()] = LineRule(value.lower(), group, section, key)

        for key, rule in self.items():
            if rule.sortkey:
                self.sortkey = key
                break
        self.required = tuple([k for k, v in self.items() if v.required])



#==============================================================================
#
#==============================================================================

class LineRule(object):
    """LineRule(value)
    A object representing a set of rules arguments to parse a ini line with. Your
    code will never need to manually create these, they are generated automatically
    when parsing sections of the parser rule files in SectionRules()
    """
    required = False # key is required
    multiline = False # key can be multilined
    sortkey = 0 # the type of sortkey used
    args = None # tuple of RuleArg objects (these are named tuples)
    local_matches = False
    optional_index = None # the index of a RuleArg with the -o option specified


    def __init__(self, value, group, section, key):
        data = COMMA_SPLIT_RE.split(value) # split rule by comma
        flags = data.pop(0) # first argument in line rule is our flags
        flags = flags.split('|')

        unknown = tuple([f for f in flags if f not in _VALIDFLAGS])
        if unknown:
            raise RuleFileError("Unknown flags: %s" % str(unknown),
                                group, section, key)

        self.required = 'req' in flags
        self.multiline = 'multi' in flags
        if 'uglobal' in flags:
            self.sortkey = GLOBAL_UNIQUE
        if 'ugroup' in flags:
            self.sortkey = GROUP_UNIQUE
        if 'usection' in flags:
            self.sortkey = SECTION_UNIQUE
        if 'ulocal' in flags:
            self.sortkey = LOCAL_UNIQUE
        if 'uhash' in flags:
            self.sortkey = HASH_UNIQUE
        if 'local' in flags:
            self.local_matches = True

        args = []
        for index, arg in enumerate(data):
            rule_args = arg.split(' ') # split type/modifiers and options
            rule_type, count = OPTION_RE.match(rule_args.pop(0)).groups()

            if _checkFunc(rule_type) is None:
                raise RuleFileError("Unknown rule type argument: %s" % rule_type,
                                    group, section, key)

            options = {}
            for rule_opt in rule_args:
                k, v = _parseOption(rule_opt, group, section, key)
                options[k] = v
            optional = options.get('optional', 0)

            if optional and self.optional_index is not None:
                raise RuleFileError("Cant have more then 1 optional arg per line.",
                                    group, section, key)
            elif optional:
                self.optional_index = index

            if count and count == '+' or count == '*':
                count = -1
                if not optional:
                    raise RuleFileError('Non-optional unlimted argument count.',
                                        group, section, key)
            elif count:
                count = int(count[1:])
            else:
                count = 1

            args.append(RuleArg(rule_type, count, options))
        self.args = tuple(args)


    def check(self, ini, index, key, value, match_check=False):
        """LineRule.check(ini, index, key, value)
        Compares the data in a FL ini line with the rules associated with the
        Group:Section:Key. It is not nessessary to manually call this method, it
        is called automatically when parsing a DataFile and freelancer.settings.validate_rules
        is set to True.
        """
        data = COMMA_SPLIT_RE.split(value)
        expected = self._getExpected(data)

        for expected_index, arg_index in enumerate(expected):
            arg = self.args[arg_index]
            options = arg.options
            call = _checkFunc(arg.type) # our checking function to call

            try:
                value = data[expected_index]
            except IndexError:
                # TODO: inc error count
                log.warn("FLData: Missing %s value (key:%s arg:#%s) in file %s (line %s)" % 
                         (arg.type, key, expected_index, ini.parent.path, index + ini.index))
                break

            stats_inc(STATS_ARGS, 1) # increment total # of args
            if not call(value, options):
                # TODO: inc error count
                log.warn("FLData: Non matching %s value (key:%s arg:#%s) '%s' in file %s (line %s)" % 
                         (arg.type, key, expected_index, value, ini.parent.path, index + ini.index))
            #else:
            #    if call == _cmpIdsString:
            #        resources.addNameRef(int(value), ini, index, expected_index)
            #    elif call == _cmpIdsHtml:
            #        resources.addInfoRef(int(value), ini, index, expected_index)


            if options.get('max') is not None and float(value) > options['max']:
                # TODO: inc error count
                log.warn("FLData: Value %s is above max (key:%s arg:#%s) in file %s (line %s)" % 
                         (value, key, expected_index, ini.parent.path, index + ini.index))
                #ini.error(index, "Value %s is above max (%s #%s) '%s'" % (value, key, expected_index, value))
            if options.get('min') is not None and float(value) < options['min']:
                # TODO: inc error count
                log.warn("FLData: Value %s is below min (key:%s arg:#%s) in file %s (line %s)" % 
                         (value, key, expected_index, ini.parent.path, index + ini.index))
                #ini.error(index, "Value %s is below min (%s #%s) '%s'" % (value, key, expected_index, value))

            if options.get('match') and match_check:
                queue_match((ini, index, options['match'], self.local_matches, value.lower()))

        if len(data) > len(expected):
                # TODO: inc error count
            log.warn("FLData: Too many values for key %s in file %s (line %s)" %
                     (key, ini.parent.path, index + ini.index))
            #ini.error(index, "Too many values on line")


    def _getExpected(self, data):
        """LineRule._getExpected(data)
        Internal method. Compares the arguments in the LineRule with the arguments
        in data (a list of values in a DataFile line) and decides what RuleArg to
        compare each value with. Returns a list of RuleArg indexes.
        """
        compare = []
        optional_index = None # our spot in the compare list to insert
        for index, arg in enumerate(self.args):
            if index == self.optional_index:
                optional_index = len(compare)
            else:
                _ = [compare.append(index) for _ in range(arg.count)]

        difference = len(data) - len(compare)
        if optional_index is None:
            return compare

        # insert optional args
        arg = self.args[self.optional_index]
        if arg.count == -1:
            #insert the difference, note this one 'should' always be at the end
            compare[optional_index:optional_index] = [self.optional_index for _ in range(difference)]
        elif difference >= arg.count:
            # we seem to have extra args in the data, so only insert what this rule allows
            compare[optional_index:optional_index] = [self.optional_index for _ in range(arg.count)]
        else:
            # rule allows for more args then we have, so only insert some
            insert = arg.count - (arg.count - arg.options.get('optional') + 1)
            compare[optional_index:optional_index] = [self.optional_index for _ in range(insert)]
        return compare


def _parseOption(opt, group, section, key):
    """_parseOption(opt)
    Internal function. Called when building a LineRule object. Validates a - or --
    option in the rules. Returns a tuple for building the options dict (key, value)
    """
    result = None
    if opt.startswith('-o='):
        try:
            result = ('optional', int(opt[3:]))
        except (ValueError, IndexError):
            raise RuleFileError("-o option requires a integer value.", group, section, key)

    elif opt == '-o':
        result = ('optional', 1)

    elif opt.startswith('--max='):
        try:
            result = ('max', float(opt[6:]))
        except (ValueError, IndexError):
            raise RuleFileError("--max option requires a integer or float value.", group, section, key)

    elif opt.startswith('--min='):
        try:
            result = ('min', float(opt[6:]))
        except (ValueError, IndexError):
            raise RuleFileError("--min option requires a integer or float value.", group, section, key)

    elif opt.startswith('--match='):
        try:
            result = ('match', opt[8:])
        except IndexError:
            raise RuleFileError("--match option requires something to match against.", group, section, key)

    elif opt.startswith('-m='):
        try:
            result = ('match', opt[3:])
        except IndexError:
            raise RuleFileError("-m option requires something to match against.", group, section, key)

    elif opt.startswith('-r='):
        try:
            result = ('regex', re.compile(opt[4:-1], re.I))
        except IndexError:
            raise RuleFileError("-r option requires something to match against.", group, section, key)

    elif opt.startswith('-t='):
        try:
            result = ('template', opt[3:])
        except IndexError:
            raise RuleFileError("-t option requires a parser rule template.", group, section, key)

    elif opt.startswith('-d='):
        try:
            result = ('dir', opt[3:])
        except IndexError:
            raise RuleFileError("-d option requires a directory to search.", group, section, key)

    else:
        raise RuleFileError("Unknown rule option: %s " % opt, group, section, key)
    return result


def _checkFunc(rule_type):
    """_checkFunc(rule_type)
    Internal function. Used to compare rule_type with the desired checking function.
    """
    if rule_type == 'bool':
        return _cmpBool
    elif rule_type == 'byte':
        return _cmpByte
    elif rule_type == 'int':
        return _cmpInt
    elif rule_type == 'float':
        return _cmpFloat
    elif rule_type == 'ids_string':
        return _cmpIdsString
    elif rule_type == 'ids_html':
        return _cmpIdsHtml
    elif rule_type == 'arch':
        return _cmpArch
    elif rule_type == 'word':
        return _cmpWord
    elif rule_type == 'file':
        return _cmpFile
    elif rule_type == 'ini':
        return _cmpIni
    elif rule_type == 'cmp':
        return _cmpCmp
    elif rule_type == 'mat':
        return _cmpMat
    elif rule_type == 'wav':
        return _cmpWav
    elif rule_type == 'ale':
        return _cmpAle
    elif rule_type == 'thn':
        return _cmpThn
    elif rule_type == 'string':
        return _cmpString
    return None

def _cmpBool(val, opt):
    """_cmpBool(val, opt)
    Internal function. Used for rule bool argument comparison.
    """
    return BOOL_RE.match(val) and True or False

def _cmpByte(val, opt):
    """_cmpByte(val, opt)
    Internal function. Used for rule byte argument comparison.
    """
    # TODO: some byte values are valid as floats between 0.0 and 1.0 (colors?)
    try:
        v = (0 <= int(val) <= 255)
    except ValueError:
        return False
    return v

def _cmpInt(val, opt):
    """_cmpInt(val, opt)
    Internal function. Used for rule integer argument comparison.
    """
    try:
        int(val)
    except ValueError:
        return False
    return True

def _cmpFloat(val, opt):
    """_cmpFloat(val, opt)
    Internal function. Used for rule float argument comparison.
    """
    try:
        float(val)
    except ValueError:
        return False
    return True

def _cmpIds(val, opt):
    """_cmpIds(val, opt)
    Internal function. Used for rule ids argument comparison.
    """
    return _cmpInt(val, opt)

def _cmpIdsString(val, opt):
    """_cmpIdsString(val, opt)
    Internal function. Used for rule ids argument comparison.
    """
    return _cmpInt(val, opt)

def _cmpIdsHtml(val, opt):
    """_cmpIdsHtml(val, opt)
    Internal function. Used for rule ids argument comparison.
    """
    return _cmpInt(val, opt)

def _cmpArch(val, opt):
    """_cmpArch(val, opt)
    Internal function. Used for rule arch argument comparison.
    """
    return ARCH_RE.match(val) and True or False

def _cmpWord(val, opt):
    """_cmpWord(val, opt)
    Internal function. Used for rule word argument comparison.
    """
    try:
        return opt['regex'].match(val) and True or False
    except KeyError:
        return True

def _cmpFile(val, opt):
    """_cmpFile(val, opt)
    Internal function. Used for rule file argument comparison.
    Adds file to the referenced list.
    """
    path = join('data', opt.get('dir', '').lower(), val.lower())
    add_reference(path)
    return exists(join(s_general['path'], path))

def _cmpIni(val, opt):
    """_cmpIni(val, opt)
    Internal function. Used for rule ini argument comparison.
    Adds file to the referenced list, and loads it if parse_referenced_files is set.
    """
    if _cmpFile(val, opt):
        if s_general.get('parse_referenced_files', False, dtype=bool):
            pth = join(opt.get('dir', '').lower(), val.lower())
            queue_file(opt.get('template').lower(), pth)
        return True
    return False

def _cmpCmp(val, opt):
    """_cmpCmp(val, opt)
    Internal function. Used for rule cmp argument comparison.
    """
    val = val.lower()
    return _cmpFile(val, opt) and (val.endswith('.cmp')
                                   or val.endswith('.3db')
                                   or val.endswith('.sph'))

def _cmpMat(val, opt):
    """_cmpMat(val, opt)
    Internal function. Used for rule mat argument comparison.
    """
    val = val.lower()
    return _cmpFile(val, opt) and (val.endswith('.mat') or val.endswith('.txm'))

def _cmpWav(val, opt):
    """_cmpWav(val, opt)
    Internal function. Used for rule wav argument comparison.
    """
    val = val.lower()
    return _cmpFile(val, opt) and val.endswith('.wav')

def _cmpAle(val, opt):
    """_cmpAle(val, opt)
    Internal function. Used for rule ale argument comparison.
    """
    val = val.lower()
    return _cmpFile(val, opt) and val.endswith('.ale')

def _cmpThn(val, opt):
    """_cmpThn(val, opt)
    Internal function. Used for rule thn argument comparison.
    """
    val = val.lower()
    return _cmpFile(val, opt) and val.endswith('.thn')

def _cmpString(val, opt):
    """_cmpString(val, opt)
    Internal function. Used for rule string argument comparison.
    """
    return True

def get_rules(group, section):
    return _RULES[group][section]

def load_rule_file(path, filename):
    """load_rule_file(filename)
    Mostly Internal function. Called by load_rules() to load a specific rule file"""
    # create a rule group for this file
    group = filename[:-4].lower()
    _RULES[group] = {}

    # read the file
    fih = open(join(path, filename))
    lines = fih.read()
    fih.close()
    lines = re.split('\n', lines)

    last = [] # data between [sections]
    section = None # [section] name

    for line in lines:
        line = LINE_TRIM_RE.sub('', line)

        # check for a new section
        match = SECTION_RE.match(line)
        if match and not section is None:
            # new section start, store previous data
            SectionRules(group, section, last)

        if match: # reset variables and store new name
            section = match.group(1).lower()
            last = []
            continue

        if not section is None: # data in between sections
            last.append(line)

    if section: # store last section in file
        SectionRules(group, section, last)



def load_rules(settings):
    """load_rules()
    Loads all parser rule .ini files"""
    global s_general
    s_general = settings
    path = s_general['rules_path']
    files = os.listdir(path)
    for name in files:
        if not name[-4:] == '.ini':
            continue
        load_rule_file(path, name)

