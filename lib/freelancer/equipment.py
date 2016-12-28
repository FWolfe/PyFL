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
    freelancer.equipment - Helper functions for dealing with equipment
"""
# pylint: disable=C0301
# pylint: disable=C0103

#from freelancer.bin import findHash
from freelancer.core.resources import ids_name, ids_info
from freelancer.core.data import get_group, get_sections, get_key
#from freelancer.core.data import get_sections
#from freelancer.func import idsName
#import freelancer.exceptions as flex

def get_equipment(nickname):
    """getEquipment(nickname)
    Returns a DataSection() object for the specified equipment.
    """
    for sections in get_group('equipment').values():
        if sections.has_key(nickname):
            return sections[nickname]
    return None # ("No sortkey named %s in Equipement:*" % nickname)



# =============================================================================

def get_armor(nickname=None):
    """getArmor(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'armor')
    return get_key('equipment', 'armor', nickname)


def get_attachedfx(nickname=None):
    """getAttachedFx(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'attachedfx')
    return get_key('equipment', 'attachedfx', nickname)


def get_cargopod(nickname=None):
    """getCargoPod(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'cargopod')
    return get_key('equipment', 'cargopod', nickname)


def get_cloakingdevice(nickname=None):
    """getCloakingDevice(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'cloakingdevice')
    return get_key('equipment', 'cloakingdevice', nickname)


def get_commodity(nickname=None):
    """getCommodity(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'commodity')
    return get_key('equipment', 'commodity', nickname)


def get_countermeasure(nickname=None):
    """getCounterMeasure(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'countermeasure')
    return get_key('equipment', 'countermeasure', nickname)


def get_countermeasuredropper(nickname=None):
    """getCounterMeasureDropper(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'countermeasuredropper')
    return get_key('equipment', 'countermeasuredropper', nickname)


def get_engine(nickname=None):
    """getEngine(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'engine')
    return get_key('equipment', 'engine', nickname)


def get_explosion(nickname=None):
    """getExplosion(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'explosion')
    return get_key('equipment', 'explosion', nickname)


def get_gun(nickname=None):
    """getGun(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'gun')
    return get_key('equipment', 'gun', nickname)


def get_internalfx(nickname=None):
    """getInternalFx(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'internalfx')
    return get_key('equipment', 'internalfx', nickname)


def get_light(nickname=None):
    """getLight(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'light')
    return get_key('equipment', 'light', nickname)


def get_lootcrate(nickname=None):
    """getLootCrate(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'lootcrate')
    return get_key('equipment', 'lootcrate', nickname)


def get_mine(nickname=None):
    """getMine(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'mine')
    return get_key('equipment', 'mine', nickname)


def get_minedropper(nickname=None):
    """getMineDropper(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'minedropper')
    return get_key('equipment', 'minedropper', nickname)


def get_motor(nickname=None):
    """getMotor(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'motor')
    return get_key('equipment', 'motor', nickname)


def get_munition(nickname=None):
    """getMunition(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'munition')
    return get_key('equipment', 'munition', nickname)


def get_power(nickname=None):
    """getPower(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'power')
    return get_key('equipment', 'power', nickname)


def get_repairkit(nickname=None):
    """getRepairKit(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'repairkit')
    return get_key('equipment', 'repairkit', nickname)


def get_scanner(nickname=None):
    """getScanner(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'scanner')
    return get_key('equipment', 'scanner', nickname)


def get_shield(nickname=None):
    """getShield(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'shield')
    return get_key('equipment', 'shield', nickname)


def get_shieldbattery(nickname=None):
    """getShieldBattery(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'shieldbattery')
    return get_key('equipment', 'shieldbattery', nickname)


def get_shieldgenerator(nickname=None):
    """getShieldGenerator(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'shieldgenerator')
    return get_key('equipment', 'shieldgenerator', nickname)


def get_thruster(nickname=None):
    """getThruster(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'thruster')
    return get_key('equipment', 'thruster', nickname)


def get_tractor(nickname=None):
    """getTractor(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'tractor')
    return get_key('equipment', 'tractor', nickname)


def get_tradelane(nickname=None):
    """getTradelane(nickname)
    """
    if nickname is None:
        return get_sections('equipment', 'tradelane')
    return get_key('equipment', 'tradelane', nickname)

