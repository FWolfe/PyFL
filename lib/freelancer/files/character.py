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


# pylint: disable=C0301
# pylint: disable=C0103

from os.path import join, basename, dirname, exists
from collections import namedtuple
from freelancer.core.regex import LINE_SPLIT_RE
from freelancer.core import log
from freelancer.core.settings import general
#import freelancer.func as func
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
        log.warn("Character File: %s file:" % (message, path))

class CharFile(object):
    """CharFile(accountdir, filename)
    Class representing a multiplayer character file. Unlike other files, character
    files are not automatically read and parsed when creating the object. Allowing
    the option of full reading, or just parsing/decoding the character's name.
    """
    def __init__(self, accountdir, filename):
        self.path = join(general['mp_account_path'], accountdir, filename)
        self.accountdir = accountdir
        self.charfile = filename
        self.raw = None
        self.data = None

    def isEncrypted(self):
        """CharFile.isEncrypted()
        Returns True or False if the character file is in encrypted format.
        """
        if self.raw[0:4] == 'FLS1':
            return True
        return False

    def hasLogged(self):
        """CharFile.hasLogged()
        Returns True or False if the player has actually logged, or just created the
        character.
        """
        lines = self.raw.split('\n', 3)
        if lines[2].startswith('name ='):
            return False
        return True


    def read(self, parse=True, nolog=False):
        """CharFile.read()
        Reads the character file. If parse is True will also parse it.
        """
        fi = open(self.path)
        lines = fi.read()
        fi.close()

        self.raw = lines

        if self.isEncrypted():
            raise CharFileError("Encrypted file, refusing to read", self.path, nolog)

        if not self.hasLogged():
            raise CharFileError("Character never logged, refusing to read", self.path, nolog)

        if parse:
            self.parse()


    def parseNameOnly(self):
        """CharFile.parseNameOnly()
        Parses only the description line in the character file and returns it.
        """
        lines = self.raw.split('\n', 6)
        return decodeName(lines[5][7:])


    def parse(self):
        """CharFile.parse()
        Parses the full data in the character file.
        """
        lines = self.raw.split('\n')
        data = {}
        for line in lines:
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
                if isinstance(data[key], str):
                    data[key] = [data[key], string]
                else:
                    data[key].append(string)
            except KeyError:
                data[key] = string
            if not key in KEYORDER:
                log.warn("Character File: Unknown key '%s' in file %s" % (key, self.path))
        self.data = data


    def write(self):
        """CharFile.write()
        Writes updated data to the character file.
        """
        fi = open(self.path, 'w')
        for key in KEYORDER:
            if key is '':
                fi.write('\n')
                continue

            if key[0] == '[':
                fi.write('%s\n' % key)
                continue

            value = self.data.get(key)
            if value is None:
                continue
            elif isinstance(value, (str, unicode, int, float)):
                fi.write('%s = %s\n' % (key, value))
            elif isinstance(value, list):
                for v in value:
                    fi.write('%s = %s\n' % (key, v))
            else:
                log.warn("Character File (write): invalid data type: %s %s" %
                         (type(value), repr(value)))

        fi.close()

    def getShip(self):
        return self.data.get('ship_archetype', '')
        
    def getAffiliation(self):
        return self.data.get('rep_group', '')
        
    def getRep(self, faction):
        return float(self.getAllReps()[faction])
        
    def getAllReps(self):
        results = {}
        factions = self.data.get('house')
        for line in factions:
            rep, faction = line.split(', ', 1)
            results[faction] = float(rep)
        return results

    def syncBase(self):
        """CharFile.syncBase()
        Copies the current base data and ship to the last_base keys. If the
        player isnt docked nothing is done.
        """
        data = self.data
        if not data.get('base'):
            return
        data['lastbase'] = data['base']
        if data.get('equip'):
            data['base_equip'] = data['equip']
        elif data.get('base_equip'):
            del data['base_equip']

        if data.get('cargo'):
            data['base_cargo'] = data['cargo']
        elif data.get('base_cargo'):
            del data['base_cargo']

        if data.get('hull_status'):
            data['base_hull_status'] = data['hull_status']
        elif data.get('base_hull_status'):
            del data['base_hull_status']

        if data.get('collision_group'):
            data['base_collision_group'] = data['collision_group']
        elif data.get('base_collision_group'):
            del data['base_collision_group']


def decodeName(name):
    """decodeName(name)
    Decodes the characters name from the 'description' key in the player file.
    Returns a string.
    """
    return ''.join([name[i+2:i+4] for i in xrange(0, len(name), 4)]).decode('hex')


def findCharFile(name, account=None):
    """findCharFile(name, account=None)
    Finds the character file for the given name and account directory. If account is
    None, checks all player accounts.
    Returns a CharFile() object.
    """
    path = general['mp_account_path']
    if account:
        path = join(path, account)
    cfiles = [f for f in files.list_directory(path) if f.endswith('.fl')]

    for fi in cfiles:
        np = join(path, fi)
        accountdir = basename(dirname(np))
        filename = basename(np)

        cf = CharFile(accountdir, filename)
        try:
            cf.read(parse=False, nolog=True)
        except CharFileError:
            continue
        if cf.parseNameOnly() == name:
            return cf


