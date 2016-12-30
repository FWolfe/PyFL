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
    freelancer.mbases - Helper functions for dealing with mbases.ini
"""
from freelancer.core.data import get_group_files
_MBASES = {}


def parse_mbases():
    """parse_mbases()
    Parses the mbases.ini file. Due to the structure of the file, special
    handling must be used to keep all the sections associated with the
    correct base. This assumes the IniFile for mbases.ini has already been
    loaded and parsed.
    """
    mbases = get_group_files('mbases')[0]
    this_base = []
    last_base = None
    for section in mbases:
        if section.section == 'mbase':
            if last_base:
                _MBASES[last_base] = MBase(this_base)
            last_base = section.get('nickname').lower()
            this_base = []
        this_base.append(section)
    if last_base:
        _MBASES[last_base] = MBase(this_base)

def get_base(nickname):
    """get_base(nickname)
    Returns the MBase object for the given base nickname.
    """
    return _MBASES[nickname]



class MBase(object):
    """MBase(objects)
    A class represnting a base's data sections in the mbases.ini file.
    These are created when parse_mbases() is called, so is not normally called
    manually. The inital 'objects' argument is a list of IniSection objects.
    """
    objects = None
    mbase = None
    factions = None
    missions = None
    rooms = None
    npcs = None
    def __init__(self, objects):
        self.objects = objects
        self.mbase = objects[0]
        self.factions = []
        self.rooms = []
        self.npcs = []
        for obj in objects:
            if obj.section == 'mvendor':
                self.missions = obj
            elif obj.section == 'basefaction':
                self.factions.append(obj)
            elif obj.section == 'gf_npc':
                self.npcs.append(obj)
            elif obj.section == 'mroom':
                self.rooms.append(obj)

    def get_vendors(self):
        """MBase.get_vendors()
        Returns a list of IniSection [gf_npc] objects if the nickname contains
        '_fix_' (assumes the npc is a vendor)
        """
        return [obj for obj in self.npcs if '_fix_' in obj.get('nickname')]

    def get_factions(self):
        """MBase.get_factions()
        Returns a list of all [BaseFaction] 'faction' values.
        """
        return [obj.get('faction') for obj in self.factions]

    def local_faction(self):
        """MBase.local_faction()
        Returns the base's local_faction nickname
        """
        return self.mbase.get('local_faction')

    def is_base_faction(self, faction):
        """MBase.is_base_faction(self, faction)
        Returns True if the faction nickname is listed as one of the base's
        [BaseFaction] sections.
        """
        return faction in self.get_factions()

    def get_faction_npcs(self, faction):
        """MBase.get_faction_npcs(faction)
        Returns a list of IniSection objects of all npcs affiliated with the
        the specified faction.
        """
        npcs = []
        for obj in self.npcs:
            if obj.get('affiliation').lower() == faction:
                npcs.append(obj)
        return npcs
