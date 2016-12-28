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
    freelancer.factions - Helper functions for dealing with factions
"""

from freelancer.core.resources import ids_name, ids_info
from freelancer.core.data import get_sections


def get_faction(nickname=None):
    """get_faction(nickname=None)
    Returns the DataSection() object for the specified faction. (from initialworld.ini)
    If no faction is specified returns the all faction DataSection objects
    """
    if nickname is None:
        return get_sections('groups', 'group')
    return get_key('groups', 'group', nickname)


def faction_name(name):
    """faction_name(nickname)
    Returns the ids name for the specified faction.
    """
    ids = get_faction(name).get('ids_name', dtype=int)
    return ids_name(ids)


def faction_short(name):
    """faction_short(nickname)
    Returns the short ids name for the specified faction.
    """
    ids = get_faction(name).get('ids_short_name', dtype=int)
    return ids_name(ids)


def faction_info(name):
    """faction_info(nickname)
    Returns the ids info for the specified faction.
    """
    ids = get_faction(name).get('ids_info', dtype=int)
    return ids_info(ids)


def get_rep(faction_a, faction_b):
    """get_rep(faction_a, faction_b)
    Returns a float value of faction_a's reputation with faction_b.
    """
    section = get_faction(faction_a)
    for rep in section.get('rep'):
        if rep.endswith(faction_b):
            return float(rep.split(', ')[0])


def adj_rep(faction_a, faction_b, value, min_value=-0.9, max_value=0.9):
    """adj_rep(faction_a, faction_b, value)
    Adjusts faction_a and faction_b's reputation by the amount specified in value,
    obeying the limits of min_value and max_value.
    """
    rep = get_rep(faction_a, faction_b) + value
    if rep < min_value:
        rep = min_value
    elif rep > max_value:
        rep = max_value
    set_rep(faction_a, faction_b, rep)


def set_rep(faction_a, faction_b, value, update=False):
    """set_rep(faction_a, faction_b, value)
    Sets the reputation of faction_a and faction_b to the specified value.
    """
    a = get_faction(faction_a)
    b = get_faction(faction_b)
    rep_lines = a.get('rep')
    for index, rep in enumerate(rep_lines):
        if rep.endswith(faction_b):
            rep_lines[index] = "%f, %s" % (value, faction_b)
    a.set('rep', rep_lines)

    rep_lines = b.get('rep')
    for index, rep in enumerate(rep_lines):
        if rep.endswith(faction_a):
            rep_lines[index] = "%f, %s" % (value, faction_a)
    b.set('rep', rep_lines)
    if update:
        a.parent.update()


def get_props(nickname):
    try:
        return get_sections('factionprops', 'factionprops')[nickname]
    except KeyError:
        # throw exception here "No sortkey named %s in FactionProps:FactionProps" % nickname
        return None
