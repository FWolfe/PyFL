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
    freelancer - Main freelancer module. Imports most other modules and contains
    the functions for loading freelancer's ini files.
"""

# pylint: disable=C0301
# pylint: disable=C0103

from os.path import join, splitext
import freelancer.core
#from freelancer.files.ini import IniFile, DataIniFile
#import freelancer.settings as settings
#import freelancer.files.rules

#import freelancer.files.resources as resources
#import freelancer.files.frc as frc
#import freelancer.common as common
#import freelancer.equipment as equipment
#import freelancer.factions as factions
#import freelancer.func as func
#import freelancer.ships as ships
#import freelancer.tools as tools
#import freelancer.universe as universe
#import freelancer.bin

#import freelancer.exceptions
#config = None
#settings = None
#data = common.data
# =============================================================================
#
#   File Handling Functions
#
# =============================================================================

def init(config_file='PyFL-Config.ini', minimal=False):
    """init(config_file='PyFL-Config.ini', minimal=False)
    Proxy function for freelancer.core.init()
    """
    freelancer.core.init(config_file)
    if minimal is False:
        return
    #freelancer.core.load_nonreferenced()
    #freelancer.core.load_queue()
    #freelancer.core.validate_match_queue()
    

#==============================================================================
# 
# 
# def outputStats():
#     """outputStats()
#     Outputs the stats to the logger, this should only be called after all
#     files have been loaded and checks done.
#     """
#     import time
#     sta = common.stats
#     sta[0] = time.time() - sta[0]
# 
#     common.logger("\n---------------------------------------------------")
#     text = "%s files read (%s lines), %s Sections, %s Keys and %s Arguments Parsed (%s Errors)" % (sta[1], sta[2], sta[3], sta[4], sta[5], sta[6])
#     common.logger(text)
# 
#     crf = common.referenced_files
#     text = "%s files referenced, %s times:" % (
#         len(set(crf.keys())), sum(crf.values()))
#     common.logger(text)
# 
#     # file type references
#     extensions = set([splitext(x)[1] for x in crf.keys()])
#     for fext in extensions:
#         text = "%s = %s, " % (fext, len([x for x in crf.keys() if x[-4:] == fext]))
#         common.logger(text)
#     common.logger("\n")
# 
#     # Section stats
#     cnt = [0, 0, 0, 0, 0, 0, 0, 0, 0]
#     if data.get('universe'):
#         cnt[0] = len(data['universe']['base'])
#         cnt[1] = len(data['universe']['system'])
# 
#     if data.get('groups'):
#         cnt[2] = len(data['groups']['group'])
# 
#     if data.get('ships'):
#         cnt[3] = len(data['ships']['ship'])
# 
#     if data.get('equipment'):
#         cnt[4] = len(data['equipment']['gun'])
#         cnt[5] = len(data['equipment']['minedropper'])
#         cnt[6] = len(data['equipment']['shield'])
#         cnt[7] = len(data['equipment']['power'])
#         cnt[8] = len(data['equipment']['commodity'])
# 
#     text = "%s Bases in %s Systems, %s Factions, %s Ships" % (
#         cnt[0], cnt[1], cnt[2], cnt[3])
#     common.logger(text)
# 
#     text = "%s Weapons, %s Mines, %s Shields, %s Powerplants, %s Commodities" % (
#         cnt[4], cnt[5], cnt[6], cnt[7], cnt[8])
#     common.logger(text)
# 
#     common.logger("Total Time: %s seconds" % sta[0])
#     common.logfile_handle.flush()
# 
# 
# def loadCritical():
#     """loadCritical()
#     Loads 'critical' files only. This effectively clears the load queue except
#     for files in the solars, universe, equipment, ships, goods, groups, loadouts,
#     and markets groups.
#     """
#     assert config
# 
#     valid_keys = ('solars', 'universe', 'equipment', 'ships', 'goods',
#                   'groups', 'loadouts', 'markets')
#     common.file_queue = [f for f in common.file_queue if f[0] in valid_keys]
#     loadQueue()
# 
# 
# def loadUniverse():
#     """loadUniverse()
#     Loads the Universe.ini, and any systems files. This is the only method to
#     load the systems files when freelancer.settings.parse_referenced_files
#     is set to False.
#     """
#     assert config
# 
#     common.file_queue = [f for f in common.file_queue if f[0] == 'universe']
#     loadQueue()
#     for sobj in data['universe']['system'].values():
#         common.file_queue.append(('systems', join('universe', sobj.get('file'))))
#     loadQueue()
# 
# 
# def loadAll():
#     """loadAll()
#     Loads all files in the queue, and sets the 'loaded_everything' flag if
#     freelancer.settings.parse_referenced_files is True.
#     """
#     assert config
#     settings.parse_referenced_files = True
#     settings.perform_match_checks = True
#     settings.validate_rules = True
#     common.loaded_everything = True
#     loadQueue()
#     loadNonReferenced()
# 
# 
# def loadNonReferenced():
#     """loadNonReferenced()
#     Loads non-referenced files. Specifically these files arent referenced in the
#     Freelancer.ini, or any other files, but are required by the server.
#     """
#     common.file_queue = [] # clear our queue
#     for key, val in common.nonreferenced.items():
#         for fil in val:
#             common.file_queue.append((key, fil))
#     loadQueue()
# 
# 
# def writeSummaries():
#     """writeSummaries()
#     Writes the various summary files of the mod content.
#     """
#     if not settings.write_summaries:
#         return
# 
#     if common.loaded_everything:
#         unused = func.findNotUsedFiles()
#         fih = open(settings.unused_summary, 'w')
#         common.logger("%s Unused Files" % len(unused))
#         for fil in unused:
#             fih.write("%s\n" % fil)
#         fih.close()
# 
#     common.logger("Writing System Summary....")
#     tools.summarizeSystems()
# 
#     common.logger("Writing Faction Summary....")
#     tools.summarizeFactions()
# 
#==============================================================================
