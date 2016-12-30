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
    freelancer.systems - Helper functions for dealing with system files
"""

from os.path import join
from freelancer.core.data import get_key, get_data_file
from freelancer.core.resources import ids_name
import freelancer.mbases as mbases

def _from_universe(system_name):
    """_from_universe(system_name)
    Internal Function. Gets the [System] section from universe.ini
    """
    return get_key('universe', 'system', system_name)


def get_system(system_name):
    """get_system(system_name)
    Returns the IniFile object for the specified system.
    """
    return get_data_file(join('universe', _from_universe(system_name)['file']))


def get_zones(system_name):
    """get_zones(system_name)
    Returns the a list of [Zone] IniSection() objects in the specified system.
    """
    return get_system(system_name).findall('zone')


def get_jumps(system_name):
    """get_jumps(system_name)
    Returns the a list of jump targets (system nicknames) for all jumps in the 
    specified system ('goto' key).
    """
    system = get_system(system_name)
    jumps = [obj for obj in system.findall('object') if obj.get('goto')]
    jumps = [obj.get('goto').split(',')[0] for obj in jumps]
    jumps.sort()
    return jumps


def get_local_faction(system_name):
    """get_local_faction(system_name)
    Returns the [SystemInfo] 'local_faction' value for the specified system.
    """
    return get_system(system_name).find('systeminfo').get('local_faction')


def get_factions(system_name):
    """get_factions(system_name)
    Finds all factions in a system. Returns a multi dimensional list:
    [local_faction, [factions that own objects], [factions that have a npc presence]]
    """
    owned = []
    presence = []
    system = get_system(system_name)
    for section in system:
        # facions that own objects
        rep = section.get('reputation')
        if rep:
            owned.append(rep.lower())
        # factions with presence
        faction_list = section.get('faction') # this line needs splitting
        if not faction_list:
            continue
        for faction in faction_list:
            presence.append(faction.split(',')[0].lower())

    return [get_local_faction(system_name), set(owned), set(presence)]


def get_faction_objects(system_name, faction):
    """get_faction_objects(system_name, faction)
    Finds and returns a list of IniSection objects in a system owned by the
    specified faction. ('reputation' key is set)
    """
    obj = []
    system = get_system(system_name)
    for section in system:
        rep = section.get('reputation')
        if not rep:
            continue
        if rep.lower() == faction:
            obj.append(section)
    return obj



def is_dockable(system_name, object_name, faction=None):
    """is_dockable(system_name, object_name, faction=None)
    Returns True or False depending on the values of object_name and faction:
    If object_name is a jumpgate, returns True
    If object_name is a base and faction is None, returns True
    If object_name is a base and faction is NOT None, returns True IF faction
    is listed as a [BaseFaction] in mbases.ini
    """
    system = get_system(system_name)
    obj = system.keymap[object_name.lower()]
    if obj.get('goto'): # jumpgate
        # TODO: rep check if faction is not None...is this gate hostile?
        # is the far gate hostile?
        return True

    dock = obj.get('base', obj.get('dock_with', None))
    if not dock:
        return False
    if faction is None:
        return True
    if mbases.get_base(dock).is_base_faction(faction):
        return True
    return False


def get_obj_base(system_name, object_name):
    """get_obj_base(system_name, object_name)
    Returns the base nickname associated with the given object_name
    If the object doesn't have a 'base' or 'dock_with' key, returns None
    """
    system = get_system(system_name)
    obj = system.keymap[object_name.lower()]
    return obj.get('base', obj.get('dock_with', None))


