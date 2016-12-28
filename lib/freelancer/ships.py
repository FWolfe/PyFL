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
    freelancer.ships - Helper functions for dealing with ships
"""


from freelancer.core.resources import ids_name, ids_info
from freelancer.core.data import get_sections, get_key


def get_ship(nickname=None):
    """getShip(nickname)
    Returns the DataSection() object for the specified ship, usually from the 
    shiparch.ini.
    """
    if nickname is None:
        return get_sections('ships', 'ship')
    return get_key('ships', 'ship', nickname)


def get_name(nickname):
    """getShipName(nickname)
    Returns ids name for the specified ship nickname
    """
    ids = get_ship(nickname).get('ids_name')
    return ids_name(ids)


def loadout_mass(nickname):
    """loadout_mass(nickname)
    Calculates the mass for the given loadout nickname. Returns the sum of the
    equipment and cargo as a float.
    """
    from freelancer.equipment import get_equipment

    # get the loadout DataSection
    lout = get_key('loadouts', 'loadout', nickname)

    # get equipment nicknames
    equip1 = [x.split(',')[0] for x in lout.get('equip', [])]
    # fetch DataSection objects
    equip = [get_equipment(x) for x in equip1]
    # get the mass
    equip = [x.get('mass', 0, dtype=float) for x in equip]

    # repeat for cargo
    cargo = [x.split(',') for x in lout.get('cargo', [])]
    cargo = [(get_equipment(x[0]), x[1]) for x in cargo]
    cargo = [x.get('mass', 0, dtype=float)*int(y) for x, y in cargo]
    
    # note...archetype = ship_name in [loadout] doesnt really matter...
    # loadouts arent bound to specific ships.
    return sum(equip) + sum(cargo)


def ship_mass(nickname, loadout=None):
    """ship_mass(nickname, loadout=None)
    Returns the mass for the shiphull, plus loadout if specified
    """
    mass = get_ship(nickname).get('mass', 0, dtype=float)
    if loadout:
        return mass + loadout_mass(loadout)
    return mass

#==============================================================================
# 
# def find_ships(key, value):
#     """find_ships(key, value)
#     Returns a list of all ships that have a key that matches a specified value.
#     The value argument maybe a function, in which case it should accept a 
#     single argument (the value to compare) and return a bool value.
#     """
#     ships = get_sections('ships', 'ship').values()
#     if callable(value):
#         return [ship for ship in ships if value(ship.get(key))]
#     return [ship for ship in ships if ship.get(key, default='').lower() == value]
# 
# 
#==============================================================================
