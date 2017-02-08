# -*- coding: utf-8 -*-
# =============================================================================
#
#    Copyright (C) 2015  Fenris_Wolf, YSPStudios
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
    freelancer.embedded - Module for use by FLHook's embedded python plugin.

    This module handles FLHook's callbacks, struct to namedtuple conversions, and defines enum constants 
    such as HK_ERROR and PLUGIN_RETURNCODE values for use in modules.
    
    Outside of FLHook C++ code, there are no usable python functions here, though the constants are useful.
    FLHooks callbacks are all routed to the pluginsystem module as PluginList.sigOut() calls
    
"""
# pylint: disable=C0301
# pylint: disable=C0103

import FLHook # embedded module in FLHook's C++
from pluginsystem import PluginList
#from timersystem import TimerList
from freelancer.embedded.classes import convertConst, convertClass



#import freelancer.core.exceptions as flex
#import freelancer.settings as settings
#import freelancer.common


# C++ structs are converted to collections.namedtuple objects. This keeps our C++ syntax for accessing attributes like:
# Vector.x, Vector.y, etc, and ensures a 'read-only' mentality on the data

#==============================================================================
# FLHook Constants
#==============================================================================
HKE_OK = 0
HKE_PLAYER_NOT_LOGGED_IN = 1
HKE_CHAR_DOES_NOT_EXIST = 2
HKE_COULD_NOT_DECODE_CHARFILE = 3
HKE_COULD_NOT_ENCODE_CHARFILE = 4
HKE_INVALID_BASENAME = 5
HKE_UNKNOWN_ERROR = 6
HKE_INVALID_CLIENT_ID = 7
HKE_INVALID_GROUP_ID = 8
HKE_INVALID_ID_STRING = 9
HKE_INVALID_SYSTEM = 10
HKE_PLAYER_NOT_IN_SPACE = 11
HKE_PLAYER_NOT_DOCKED = 12
HKE_PLAYER_NO_ADMIN = 13
HKE_WRONG_XML_SYNTAX = 14
HKE_INVALID_GOOD = 15
HKE_NO_CHAR_SELECTED = 16
HKE_CHARNAME_ALREADY_EXISTS = 17
HKE_CHARNAME_TOO_LONG = 18
HKE_CHARNAME_TOO_SHORT = 19
HKE_AMBIGUOUS_SHORTCUT = 20
HKE_NO_MATCHING_PLAYER = 21
HKE_INVALID_SHORTCUT_STRING = 22
HKE_MPNEWCHARACTERFILE_NOT_FOUND_OR_INVALID = 23
HKE_INVALID_REP_GROUP = 24
HKE_COULD_NOT_GET_PATH = 25
HKE_NO_TASKKILL = 26
HKE_SYSTEM_NO_MATCH = 27
HKE_OBJECT_NO_DOCK = 28
HKE_CARGO_WONT_FIT = 29
HKE_NAME_NOT_MATCH_RESTRICTION = 30


#==============================================================================
# PLUGIN_RETURNCODE
DEFAULT_RETURNCODE = 0
SKIPPLUGINS = 1
SKIPPLUGINS_NOFUNCTIONCALL = 2
NOFUNCTIONCALL = 3


#==============================================================================
# ENGINE_STATE
ES_CRUISE = 0
ES_THRUSTER = 1
ES_ENGINE = 2
ES_KILLED = 3
ES_TRADELANE = 4

#==============================================================================
# EQ_TYPE
ET_GUN = 0
ET_TORPEDO = 1
ET_CD = 2
ET_MISSILE = 3
ET_MINE = 4
ET_CM = 5
ET_SHIELDGEN = 6
ET_THRUSTER = 7
ET_SHIELDBAT = 8
ET_NANOBOT = 9
ET_MUNITION = 10
ET_ENGINE = 11
ET_OTHER = 12
ET_SCANNER = 13
ET_TRACTOR = 14
ET_LIGHT = 15

#==============================================================================
#
#==============================================================================
config = None
plugins = PluginList(None, 'python_plugins') # First value should be None, second is the folder of our plugins
plugins.name = 'FLHook' 
plugins.debug = False # If true, all data passed through pluginsystem is send to plugins.log()

#timers = TimerList()
# We can define events that are always logged, or never logged. Anything not defined here is logged based on
# the plugins.debug setting above
plugins.logtypes = {
    'HkCbIServerImpl_Update' : False,
    'HkCbIServerImpl_SPObjUpdate' : False,
    'HkCbIServerImpl_SPObjUpdate_AFTER' : False,
    'HkCbIServerImpl_ActivateThrusters' : False,
    'HkCbIServerImpl_ActivateThrusters_AFTER' : False,
    'HkCbIServerImpl_ActivateEquip' : False,
    'HkCbIServerImpl_ActivateEquip_AFTER' : False,
    'HkCbIServerImpl_FireWeapon' : False,
    'HkCbIServerImpl_FireWeapon_AFTER' : False,
    'HkCbIServerImpl_SPMunitionCollision' : False,
    'HkCbIServerImpl_SPMunitionCollision_AFTER' : False,
    'ShipDestroyed' : False, # causes buffer overflow?
    'HkTimerCheckKick' : False,
    'HkCb_Elapse_Time' : False, 
    'HkCb_Elapse_Time_AFTER' : False, 
    'HkCb_Update_Time' : False, 
    'HkCb_Update_Time_AFTER' : False, 
    'HkCb_AddDmgEntry' : False,
    'HkCb_AddDmgEntry_AFTER' : False,
    
    'HkCbIServerImpl_SetWeaponGroup' : False,
    'HkCbIServerImpl_SetWeaponGroup_AFTER' : False,
}


    

#==============================================================================
#
#==============================================================================
def logger(text):
    """logger(text)
    basic logging function"""
    FLHook.ConPrint("%s\n" % text)
    FLHook.AddLog(text)


def _load_plugins(plist):
    """_loadPlugins(plist)
    internal function called from _init() plist is a list of plugin filenames (without the .py extension)
    """
    if isinstance(plist, str):
        plist = [plist]
    logger("Loading Python Plugins...")
    for name in plist:
        if not plugins.load_plugin(name):
            FLHook.ConPrint("Python Plugin %s Failed to Load\n" % name)
        else:
            FLHook.ConPrint("Python Plugin %s Loaded\n" % name)

    
def _init():
    """_init()
    internal function called from C++, when python is starting up.
    """
    # set our plugins.log function to the logger function defined above
    plugins.log = logger
    
    # here is where any configuration files should get loaded
    # .....
    
    # PyFL stuff - OUTDATED
    #freelancer.common.logger = freelancer.common.fileLogger
    #settings.error_file = 'python.log'
    #settings.parse_referenced_files = False
    #settings.validate_rules = False
    #settings.perform_match_checks = False
    #settings.path = '..'
    #settings.rules_path = r'C:\Development\PyFL\etc\parser'
    #settings.frc_path = '../FRC'
    #settings.mp_account_path = r'C:\Documents and Settings\Fenris_Wolf\My Documents\My Games\Freelancer\Accts\MultiPlayer'
    try:
        #FLHook.ConPrint("Python Initializing PyFL...\n")
        #freelancer.init(False)
        #FLHook.ConPrint("Python Loading Data...\n")
        #freelancer.loadCritical()
        #FLHook.ConPrint("Python Loading Universe.\n")
        #freelancer.loadUniverse()
        
        #freelancer.common.logger = logger
        #freelancer.outputStats()

        FLHook.ConPrint("Python Ready.\n")
    except Exception as message:
        logger(str(message))

    
    #plist = ['example'] # this should probably be read from a config file
    plist = ['status']
    _load_plugins(plist)
    logger('Python Loaded OK!')


def _shutdown():
    """_shutdown()
    internal function called from C++, when python is shutting down.
    """
    logger("Shutting Down Python")




def _callback(event, data):
    """_callback(event, data)
    internal function called from C++, pyCallback() function. This is our main callback handler
    """
    return plugins.sigout(event, data)

