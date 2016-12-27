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
    freelancer.files - common functions for dealing with files
"""


import shutil
import json
import os
from os.path import join, dirname, exists
from zlib import crc32
#from freelancer.core import log

def list_directory(path):
    """Recursively lists all files in a directory"""
    result = []
    plen = len(path)+1
    result = [join(dp[plen:], f) for dp, _, filenames in os.walk(path) for f in filenames]
    result.sort()
    return result


def copy_file(source_folder, dest_folder, path):
    """Copies a file, creating the destination path if needed"""
    #common.logger("Copying %s" % path)
    new_path = join(dest_folder, path)
    ori_path = join(source_folder, path)
    if not exists(dirname(new_path)):
        os.makedirs(dirname(new_path))
    shutil.copy2(ori_path, new_path)


def json_load(path):
    """Loads a json file and returns the data"""
    #if not exists(path):
    #    raise flexcept.FileMissingError(path)
    fih = open(path)
    data = fih.read()
    fih.close()
    return json.loads(data)

def json_save(path, data):
    """saves data to a json file"""
    fih = open(path, 'w')
    fih.write(json.dumps(data, indent=4))
    fih.close()


def get_file_crc(path):
    """Returns the CRC value for the specified file"""
    fih = open(path, 'rb')
    result = "%x" % (crc32(fih.read()) & 0xFFFFFFFF)
    fih.close()
    return result

def get_directory_crcs(basepath, lowercase=False):
    result = {}
    for file_name in list_directory(basepath):
        if lowercase:
            file_name = file_name.lower()
        result[file_name] = get_file_crc(join(basepath, file_name))
    return result
