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

import os
import os.path
import sys
# set a local path to our freelancer python modules
sys.path[:] = [os.path.join(os.getcwd(), 'lib')] + sys.path


# =============================================================================
# Initial PyFL Imports
import freelancer.core as core
# initialize the core
core.init(config_file='PyFL-Config.ini') 
# queue all 'non-referenced' files to load
core.load_nonreferenced()
# load all files in the queue
core.load_queue()
# perform FL data cross-reference matches
core.validate_match_queue()
