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
    freelancer.core.settings - Functions and data for PyFL's configuration
    files.
"""
from freelancer.core import log as _log
import freelancer.files.ini as _ini
# pylint: disable=C0103
# pylint: disable=W0231

# these are assigned during load()
settings = None
general = None
modextractor = None
resources = None
executables = None

_DEFAULTS = {
    'general' : {
        'rules_path': r'etc\parser',
        'validate_data' : 'true',
        'parse_referenced_files' : 'true',
        'match_checks': 'true',
        'log_file' : 'PyFL.log',
        'log_stdout' : 'true',
        'log_level' : 'warn',
        'log_append' : 'true',
        'log_timestamp' : 'true',
    }
}

# these files arent actually referenced anywhere but are required
NONREFERENCED_FILES = {
    'lightanim' : (r'fx\lightanim.ini',),
    'pilots' : (
        r'missions\pilots_population.ini',
        r'missions\pilots_story.ini',
    ),
    'diff2money' : (r'randommissions\diff2money.ini',),
    'factionprops' :(r'missions\faction_prop.ini',),
    'mbases' :(r'missions\mbases.ini',),
    'formations' :(r'missions\formations.ini',),
    'lootprops' :(r'missions\lootprops.ini',),
    'empathy' : (r'missions\empathy.ini',),
    'mshipprops': (r'missions\mshipprops.ini',),

    'commodities_per_faction' : (r'equipment\commodities_per_faction.ini',),
    'goods' : (r'equipment\engine_good.ini',),
    'cameras': (r'cameras.ini',),
    'mouse' : (r'mouse.ini',),
    'soundcfg': (r'audio\soundcfg.ini',),
    'buttonmontage': (r'interface\buttonmontage.ini',),
    'shapes' : (
        r'interface\buttontextures.ini',
        r'interface\neuronet\navmap\newnavmap\navmaptextures.ini',
        r'interface\ui\uitextures.ini',
    ),
    'infocardmap' : (r'interface\infocardmap.ini',),
    'keylist' : (r'interface\keylist.ini',),
    'keymap' : (r'interface\keymap.ini',),
    'knowlagemap' : (r'interface\knowledgemap.ini',),
    'rollover' : (r'interface\rollover.ini',),
    'navbar' : (r'interface\baseside\navbar.ini',),
    'rmlootinfo' : (
        r'missions\rmlootinfo.ini',
        r'randommissions\rmlootinfo.ini',
    ),
    'news' : (r'missions\news.ini',),
    'npcships' : (r'missions\npcships.ini',),
    'ptough' : (r'missions\ptough.ini',),
    'rankdiff' : (r'missions\rankdiff.ini',),
    'shipclasses' : (r'missions\shipclasses.ini',),
    'specific_npc' : (r'missions\specific_npc.ini',),
    'voices' : (r'missions\voice_properties.ini',),
    'killablesolars' : (r'randommissions\killablesolars.ini',),
    'npcranktodiff' : (r'randommissions\npcranktodiff.ini',),
    'solarformations' : (r'randommissions\solarformations.ini',),
    'vignettecriticalloot' : (r'randommissions\vignettecriticalloot.ini',),
    'vignetteparams' : (r'randommissions\vignetteparams.ini',),
    'gcsexcl' : (r'scripts\gcs\gcsexcl.ini',),
    'genericscripts' : (r'scripts\gcs\genericscripts.ini',),
    'missioncreatedsolars' : (r'universe\missioncreatedsolars.ini',),
    'paths' : (
        r'universe\shortest_illegal_path.ini',
        r'universe\shortest_legal_path.ini',
        r'universe\systems_shortest_path.ini',
    ),
}


#==============================================================================
#
#==============================================================================
class ConfigurationError(Exception):
    """ConfigurationError
    Exception thrown on general configuration errors. This is fatal if not
    caught and generates a ERROR in the logs.
    """
    def __init__(self, message):
        _log.error("Config: %s" % message)

class FatalConfigurationError(Exception):
    """FatalConfigurationError
    Exception thrown on general configuration errors. This is ALWAYS fatal
    and generates a CRITICAL in the logs.
    """
    def __init__(self, message, use_log=True):
        message = "Config: %s" % message
        if use_log:
            _log.critical(message)
        else:
            print message
        exit()
#==============================================================================
#
#==============================================================================
def load(filename):
    """load(filename)
    Loads the specified filename as a IniFile object. This basically init's
    this module and should be one of the first things called. Its normally
    handled by freelancer.core.init()
    """
    global settings, general, resources, executables
    # TODO: Error handling note we cant properly log anything til after the
    # logger is loaded.  Unfortuantly the logger cant load until after settings

    settings = _ini.IniFile(filename)
    for section, defaults in _DEFAULTS.items():
        obj = settings.find(section)
        if obj is None:
            continue
        for key, value in defaults.items():
            obj[key] = obj.get(key, value)
    
    general = settings.find('general') 
    if not general:
        raise FatalConfigurationError("[General] section is missing", False)

    if not general.get('mp_account_path'):
        try:
            # try to find the mp accounts ourself
            import ctypes.wintypes
            buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(0, 5, 0, 0, buf)
            general['mp_account_path'] = r"%s\%s" % (buf.value, "My Games\Freelancer\Accts\MultiPlayer")
        except ImportError:
            pass
    # pass the settings on to freelancer.files.ini since it cant import them
    _ini.s_general = general

    resources = settings.find('resources')
    executables = settings.find('executables')

def get_section(section):
    """get_section(section)
    Returns the IniSection object for the specified section name, or raises a
    ConfigurationError if it doesnt exist
    """
    sec = settings.find(section.lower())
    if sec is None:
        raise ConfigurationError("[%s] section is missing" % section)
    return sec

def get_setting(section, key, default=None, dtype=None):
    """get_setting(section, key, default=None)
    Returns the specified key from the section name or default. Raises a 
    ConfigurationError if the section doesnt exist.
    """
    sec = get_section(section)
    return sec.get(key, default=default, dtype=dtype)

def validate():
    """validate()
    Validates the contents of the PyFL config
    """
    from os.path import exists

    if not general.has_key('path'):
        raise FatalConfigurationError('[General] path key is missing.')
    if not exists(general['path']):
        raise FatalConfigurationError('[General] path is not a valid directory.')

    if not general.has_key('rules_path'):
        raise FatalConfigurationError('[General] rules_path key is missing.')
    if not exists(general['rules_path']):
        raise FatalConfigurationError('[General] rules_path is not a valid directory.')
