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
    ModExtractor.py - A reverse FLMM
    Copyright (C) 2016  Fenris_Wolf, YSPStudios
    
    Extracts all non-vanilla files from a installed mod to a seperate directory
    Also checks the previously extracted mod and copies any new or changed
    files and copies those to a patch directory.
    The idea is to simplify the modding process, as files can be worked on
    'in place' without having to remember whats changed, or working in a 
    external directory and having to activate/copy your mod into your FL
    directory each time for testing.
"""

import os
from os.path import join, isdir
import sys

# Assume we're running from PyFL\scripts directory
os.chdir('..') 

# Initial path setup python uses to look for the PyFL modules.
# set a local path to our freelancer python modules
sys.path[:] = [join(os.getcwd(), 'lib')] + sys.path

# =============================================================================
# Initial PyFL Imports
from freelancer.core import init, log, settings
from freelancer.files import get_directory_crcs, copy_file
import freelancer.files.vanilla as vanilla

files_checked = 0


# =============================================================================
# Basic functions
def finished():
    """Called on exit, pause the console to let the user know since windows likes to 
    make them disappear on finishing"""
    raw_input("Press enter to continue...")
    sys.exit()

def compare(source_path, dest_path, source_crcs, original_crcs):
    """compares all the filename and crc values in source_crcs with original_crcs.
    Any non-matching or non-existing filename is copied from source_path to dest_path
    """
    global files_checked
    copied = {}
    for filename, file_crc in source_crcs.items():
        files_checked = 1 + files_checked
        
        try:
            ocr = original_crcs[filename.lower()]
            log.debug("ModExtractor: CRC Check - %s (s: %s, d: %s)" % (filename, file_crc, ocr))
            if ocr == file_crc: # file is the same
                continue
        except KeyError: # file doesnt exist in vanilla
            pass
        copied[filename] = file_crc
        copy_file(source_path, dest_path, filename)
        log.info("ModExtractor: Copying %s" % filename)
    return copied


#==============================================================================
# MAIN CODE

# Initialize PyFL
init(config_file='PyFL-Config.ini', minimal=True)
source_path = settings.general['path']
s_extractor = settings.settings.find('modextractor')

#  Validate ModExtractor settings
if not s_extractor:
    log.critical("ModExtractor: [ModExtractor] not defined in config file")
    finished()


extract_path = s_extractor.get('extract_path')
patch_path = s_extractor.get('patch_path')
if not extract_path:
    log.critical("ModExtractor: [ModExtractor] 'extract_path' key not defined in config file")
    finished()
if not isdir(extract_path):
    log.info("ModExtractor: Creating extract directory")
    os.makedirs(extract_path)



# get a list of all mod files crcs
log.log("ModExtractor: Generating mod file crcs...")
mod_crcs = get_directory_crcs(source_path)
log.log("ModExtractor: Generating previous version crcs...")
previous_crcs = get_directory_crcs(extract_path, True)


# copy anything non-vanilla from the source
log.log("ModExtractor: Extracting mod....")
mod_crcs = compare(source_path, extract_path, mod_crcs, vanilla.CRCS)
log.log("ModExtractor: %s files checked, %s non-vanilla files copied" % 
        (files_checked, len(mod_crcs)))


# Patch Building
if not patch_path:
    log.warn("ModExtractor: [ModExtractor] patch_path key not defined, skipping path creation")
    finished()
log.log("\nModExtractor: -------------------------")
if not isdir(patch_path):
    log.info("ModExtractor: Creating patch directory")
    os.makedirs(patch_path)

files_checked = 0
log.log("ModExtractor: Extracting patch....")
mod_crcs = compare(source_path, extract_path, mod_crcs, previous_crcs)
log.log("ModExtractor: %s files checked, %s changed from previous version and copied to patch directory" % (files_checked, len(mod_crcs)))

# all done!
finished()
