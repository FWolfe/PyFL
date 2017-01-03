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
    freelancer.files.character - Helper Functions for dealing with character
    files.
"""

from os.path import join, basename, dirname
from collections import namedtuple
from freelancer.core.regex import LINE_SPLIT_RE
from freelancer.core import log
from freelancer.core.settings import general
import freelancer.files as files
Sections = namedtuple('Sections', ('header', 'rep', 'info', 'missions'))
KEYORDER = """
[Player]
description

tstamp
name
rank
house
rep_group
money
num_kills
num_misn_successes
num_misn_failures

voice
com_body
com_head
com_lefthand
com_righthand
body
head
lefthand
righthand

system
base
pos
rotate

location
ship_archetype
hull_status
collision_group

equip
cargo

last_base

base_hull_status
base_collision_group

base_equip
base_cargo

wg

visit


interface

[mPlayer]
locked_gate
vnpc
rumor
can_dock
can_tl
ship_type_killed
rm_completed
rm_aborted
rm_failed
total_cash_earned
total_time_played
sys_visited
base_visited
holes_visited""".split('\n')

class CharFileError(Exception):
    def __init__(self, message, path, nolog=False):
        if nolog:
            return
        log.warn("Character File: %s file: %s" % (message, path))

class CharFile(dict):
    """CharFile(accountdir, filename)
    Class representing a multiplayer character file. Unlike other files, character
    files are not automatically read and parsed when creating the object. Allowing
    the option of full reading, or just parsing/decoding the character's name.
    """
    def __init__(self, accountdir, filename):
        dict.__init__(self)
        self.path = join(general['mp_account_path'], accountdir, filename)
        self.accountdir = accountdir
        self.charfile = filename
        self.lines = None

    def is_encrypted(self):
        """CharFile.is_encrypted()
        Returns True or False if the character file is in encrypted format.
        """
        if self.lines[0].startswith('FLS1'):
            return True
        return False

    def has_logged(self):
        """CharFile.has_logged()
        Returns True or False if the player has actually logged, or just created the
        character.
        """
        if self.lines[2].startswith('name ='):
            return False
        return True


    def read(self, parse=True, nolog=False):
        """CharFile.read(parse=True, nolog=False)
        Reads the character file. If parse is True will also parse it.
        """
        fih = open(self.path)
        lines = fih.read()
        fih.close()

        self.lines = lines.splitlines()

        if self.is_encrypted():
            raise CharFileError("Encrypted file, refusing to read", self.path, nolog)

        if not self.has_logged():
            raise CharFileError("Character never logged, refusing to read", self.path, nolog)

        if parse:
            self.parse()



    def parse(self, name_only=False):
        """CharFile.parse()
        Parses the full data in the character file.
        """
        self.clear()
        if name_only:
            return decode_name(self.lines[5][7:])

        for line in self.lines:
            if line is '':
                continue
            match = LINE_SPLIT_RE.match(line)
            if not match:
                continue

            key, value, comments = match.groups()
            if comments is None:
                comments = ''
            if value is None:
                value = ''
            string = "%s%s" % (value, comments)
            try:
                if isinstance(self[key], str):
                    self[key] = [self[key], string]
                else:
                    self[key].append(string)
            except KeyError:
                self[key] = string
            if not key in KEYORDER:
                log.warn("Character File: Unknown key '%s' in file %s" % (key, self.path))


    def write(self):
        """CharFile.write()
        Writes updated data to the character file.
        """
        fih = open(self.path, 'w')
        for key in KEYORDER:
            if key is '':
                fih.write('\n')
                continue

            if key[0] == '[':
                fih.write('%s\n' % key)
                continue

            value = self.get(key)
            if value is None:
                continue
            elif isinstance(value, (str, unicode, int, float)):
                fih.write('%s = %s\n' % (key, value))
            elif isinstance(value, list):
                for val in value:
                    fih.write('%s = %s\n' % (key, val))
            else:
                log.warn("Character File (write): invalid data type: %s %s" %
                         (type(value), repr(value)))
        fih.close()


    def get_ship(self):
        """CharFile.get_ship()
        Proxy function for self.get('ship_archetype', '')
        """
        return self.get('ship_archetype', '')


    def get_affiliation(self):
        """CharFile.get_affiliation()
        Proxy function for self.get('rep_group', '')
        """
        return self.get('rep_group', '')


    def get_rep(self, faction):
        """CharFile.get_rep()
        Proxy function for self.get_reps()[faction]
        """
        return self.get_reps()[faction]


    def get_reps(self):
        """CharFile.get_reps()
        Returns a dict of {faction_name : float} key values. The 'house' keys
        in the file.
        """
        results = {}
        factions = self.get('house')
        for line in factions:
            rep, faction = line.split(', ', 1)
            results[faction] = float(rep)
        return results


    def sync_base(self):
        """CharFile.sync_base()
        Copies the current base data and ship to the last_base keys. If the
        player isnt docked nothing is done. This is mostly useful for bugfixing.
        """
        if not self.get('base'):
            return
        self['lastbase'] = self['base']
        _get_or_del(self, 'equip', 'base_equip')
        _get_or_del(self, 'cargo', 'base_cargo')
        _get_or_del(self, 'hull_status', 'base_hull_status')
        _get_or_del(self, 'collision_group', 'base_collision_group')


def _get_or_del(this_dict, src, dest):
    """if src exits in this_dict, copy it to dest, else del dest from dict"""
    if this_dict.get(src):
        this_dict[dest] = this_dict[src]
    elif this_dict.get(dest):
        del this_dict[dest]


def decode_name(name):
    """decode_name(name)
    Decodes the characters name from the 'description' key in the player file.
    Returns a string.
    """
    return ''.join([name[i+2:i+4] for i in xrange(0, len(name), 4)]).decode('hex')


def find(name, account=None):
    """find(name, account=None)
    Finds the character file for the given name and account directory. If account is
    None, checks all player accounts.
    Returns a CharFile() object.
    """
    path = general['mp_account_path']
    for fl_file in list_all(account):
        full_path = join(path, fl_file)
        accountdir = basename(dirname(full_path))
        filename = basename(full_path)

        char = CharFile(accountdir, filename)
        try:
            char.read(parse=False, nolog=True)
        except CharFileError:
            continue
        if char.parse(name_only=True) == name:
            return char


def list_all(account=None):
    r"""list_all(account=None)
    lists all .fl files in the specified account. If account is None, returns a
    list of account\filename.fl
    """
    path = general['mp_account_path']
    if account:
        path = join(path, account)
    return [f for f in files.list_directory(path) if f.endswith('.fl')]


def list_encrypted():
    """get_all_encrypted()
    """
