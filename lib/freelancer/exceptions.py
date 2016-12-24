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


class DllLoadError(Exception) :
    pass

class ResourceLoadError(Exception) :
    pass

class FileLoadError(Exception) :
    pass

class FileParseError(Exception) :
    pass

class FileMissingError(Exception) :
    pass

class BiniFileError(Exception):
    pass

class InvalidGroupError(Exception):
    pass

class InvalidSectionError(Exception):
    pass

class InvalidSortKeyError(Exception):
    pass

class ClientIdError(Exception):
    pass

class ConfigurationError(Exception):
    pass

class FatalConfigurationError(Exception):
    pass
