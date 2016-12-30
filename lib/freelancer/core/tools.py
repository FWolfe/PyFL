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
    freelancer.core.tools - Functions for manipulating 3rd party executables.
"""
import os
from os.path import join, splitext
from subprocess import call, check_output
from freelancer.core import settings


def _getpath(exe):
    """_getpath(exe)
    Internal function. attempts to create the full path to the exe
    """
    if not settings.executables:
        return join('bin', exe)
    return join(settings.executables.get(exe, 'bin'), exe)


def extract_hashes(output_path=None):
    """extract_hashes(output_path=None)
    Uses createid.exe to generate FL hashes and returns the result. If output_path
    is specified, saves the output as well.
    """
    with open(os.devnull, 'w') as devnull:
        args = [_getpath('createid.exe'),
                '-hmn', '-oc', '-s',
                join(settings.general['path'], 'Data')]
        output = check_output(args, stderr=devnull)

    output = output.splitlines()
    #output = NEWLINE_SPLIT_RE.split(output)
    if output_path:
        fih = open(output_path, 'w')
        [fih.write(x) for x in output]
        fih.close()
    return output


def extract_frc(filename, index):
    """extract_frc(filename, index)
    Uses res2frc.exe to generate a .frc file from the resource .dll
    """
    in_path = join(settings.general['path'], 'EXE')
    out_path = settings.resources.get('frc_path', in_path)
    filename = splitext(filename)[0]
    return call([_getpath('res2frc.exe'),
                 '-o', out_path,
                 '-i', '-10',
                 '-r', str(index),
                 "-w", "4096",
                 join(in_path, filename)])


def compile_frc(filename):
    """compile_frc(filename)
    Uses frc.exe to compile a .frc file into a resource.dll
    """
    out_path = join(settings.general['path'], 'EXE')
    in_path = settings.resources.get('frc_path', out_path)
    filename = splitext(filename)[0]
    return call([_getpath('frc.exe'),
                 "-c",
                 join(in_path, filename),
                 join(out_path, filename)
                ])


def extract_7z(source, dest):
    """extract_7z(source, dest)
    Uses 7z to extract a archive.
    """
    return call([_getpath('7z.exe'),
                 "x",
                 source,
                 "-o%s" % dest
                ])


def compile_7z(source, dest):
    """extract_7z(source, dest)
    Uses 7z to create a archive.
    """
    return call([_getpath('7z.exe'),
                 "a",
                 dest,
                 source
                ])
