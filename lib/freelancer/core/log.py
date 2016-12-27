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
    freelancer.core.log - logging functions.
"""

import logging

_root = None

def info(msg ):
    _root.info(msg)

def warn(msg):
    _root.warning(msg)

def error(msg):
    _root.error(msg)

def critical(msg):
    _root.critical(msg)

def debug(msg):
    _root.debug(msg)

def exception(msg):
    _root.exception(msg)

def log(msg):
    _root.log(35, msg)

def config(options):
    import sys
    global _root
    logging.addLevelName(35, 'NOTICE')
    level = options.get('log_level', 'INFO').upper()
    if level is 'DEBUG':
        level = logging.DEBUG
    elif level is 'INFO':
        level = logging.INFO
    elif level is 'WARN':
        level = logging.WARN
    elif level is 'NOTICE':
        level = 35
    elif level is 'ERROR':
        level = logging.ERROR
    elif level is 'CRITICAL':
        level = logging.CRITICAL

    if options.get('log_timestamp', True, dtype=bool):
        formatter = logging.Formatter("%(asctime)s [%(levelname)s]  %(message)s")
    else:
        formatter = logging.Formatter("[%(levelname)s]  %(message)s")
        
    _root = logging.getLogger()
    _root.setLevel(level)
    if options.get('log_file'):
        if options.get('log_append', True, dtype=bool) is False:
            fih = open(options['log_file'], 'w')
            fih.close()
        fih = logging.FileHandler(options['log_file'])
        fih.setFormatter(formatter)
        _root.addHandler(fih)
        
    if options.get('log_stdout', True, dtype=bool):
        con = logging.StreamHandler(sys.stdout)
        con.setFormatter(formatter)
        _root.addHandler(con)
