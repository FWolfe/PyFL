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
    freelancer.regex - Contains pre-compiled regex objects commonly used by
    multiple modules
"""

import re


SECTION_RE = re.compile(r'^ *\[([^\]]+)\] *(?:;.*)?$')
LINE_COMMENT_RE = re.compile(r'[ \t]*(?:;.*)?$')

LINE_SPLIT_RE = re.compile(r'^([^=;]+?) *= *(.+?)(\W*;.*)?$')
LINE_TRIM_RE = re.compile(r'[\t ]+$')

OPTION_RE = re.compile(r'^(\w+)([\+\*]|\*[0-9]+)?$') # parser rule options
BOOL_RE = re.compile(r'^(?:1|0|true|false)$', re.I) # parser rule bool
ARCH_RE = re.compile(r'^(?:0x[0-9a-z]+|-?[0-9]+)$') # parser rule archetype
WORD_RE = re.compile(r'^\w+$') # parser rule word
STRING_RE = re.compile('^.+$') # parser rule string

COMMA_SPLIT_RE = re.compile(' *, *')
