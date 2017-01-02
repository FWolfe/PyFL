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

from freelancer.core.resources import ids_name, ids_info
from freelancer.core.data import get_group, get_sections, get_key, FLKeyError

def get_equipment(nickname):
    """get_equipment(nickname)
    Returns a DataSection() object for the specified equipment.
    """
    nickname = nickname.lower()
    for sections in get_group('equipment').values():
        if sections.has_key(nickname):
            return sections[nickname]
    raise FLKeyError("Invalid key %s" % nickname, 'equipment', '')



# =============================================================================
def _get(section, nickname):
    if nickname is None:
        return get_sections('equipment', section)
    return get_key('equipment', section, nickname)


def get_armor(nickname=None):
    """getArmor(nickname)
    """
    return _get('armor', nickname)


def get_attachedfx(nickname=None):
    """getAttachedFx(nickname)
    """
    return _get('attachedfx', nickname)


def get_cargopod(nickname=None):
    """getCargoPod(nickname)
    """
    return _get('cargopod', nickname)


def get_cloakingdevice(nickname=None):
    """getCloakingDevice(nickname)
    """
    return _get('cloakingdevice', nickname)


def get_commodity(nickname=None):
    """getCommodity(nickname)
    """
    return _get('commodity', nickname)


def get_countermeasure(nickname=None):
    """getCounterMeasure(nickname)
    """
    return _get('countermeasure', nickname)


def get_countermeasuredropper(nickname=None):
    """getCounterMeasureDropper(nickname)
    """
    return _get('countermeasuredropper', nickname)


def get_engine(nickname=None):
    """getEngine(nickname)
    """
    return _get('engine', nickname)


def get_explosion(nickname=None):
    """getExplosion(nickname)
    """
    return _get('explosion', nickname)


def get_gun(nickname=None):
    """getGun(nickname)
    """
    return _get('gun', nickname)


def get_internalfx(nickname=None):
    """getInternalFx(nickname)
    """
    return _get('internalfx', nickname)


def get_light(nickname=None):
    """getLight(nickname)
    """
    return _get('light', nickname)


def get_lootcrate(nickname=None):
    """getLootCrate(nickname)
    """
    return _get('lootcrate', nickname)


def get_mine(nickname=None):
    """getMine(nickname)
    """
    return _get('mine', nickname)


def get_minedropper(nickname=None):
    """getMineDropper(nickname)
    """
    return _get('minedropper', nickname)


def get_motor(nickname=None):
    """getMotor(nickname)
    """
    return _get('motor', nickname)


def get_munition(nickname=None):
    """getMunition(nickname)
    """
    return _get('munition', nickname)


def get_power(nickname=None):
    """getPower(nickname)
    """
    return _get('power', nickname)


def get_repairkit(nickname=None):
    """getRepairKit(nickname)
    """
    return _get('repairkit', nickname)


def get_scanner(nickname=None):
    """getScanner(nickname)
    """
    return _get('equipment', nickname)


def get_shield(nickname=None):
    """getShield(nickname)
    """
    return _get('shield', nickname)


def get_shieldbattery(nickname=None):
    """getShieldBattery(nickname)
    """
    return _get('shieldbattery', nickname)


def get_shieldgenerator(nickname=None):
    """getShieldGenerator(nickname)
    """
    return _get('shieldgenerator', nickname)


def get_thruster(nickname=None):
    """getThruster(nickname)
    """
    return _get('thruster', nickname)


def get_tractor(nickname=None):
    """getTractor(nickname)
    """
    return _get('tractor', nickname)


def get_tradelane(nickname=None):
    """getTradelane(nickname)
    """
    return _get('tradelane', nickname)

