# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 10:51:59 2016

@author: Fenris_Wolf
"""
import os
from os.path import join, splitext
from subprocess import call, check_output
from freelancer.core import settings 


def _getpath(exe):
    if not settings.executables:
        return join('bin', exe)
    return join(settings.executables.get(exe, 'bin'), exe)


def extract_hashes(output_path=None):
    with open(os.devnull, 'w') as devnull:
        args = [_getpath('createid.exe'), '-hmn', '-oc', '-s', join(settings.general['path'], 'Data')]
        output = check_output(args, stderr=devnull)
    output = output.splitlines()
    #output = NEWLINE_SPLIT_RE.split(output)
    if output_path:
        fih = open(output_path, 'w')
        [fih.write(x) for x in output]
        fih.close()
    return output


def extract_frc(filename, index):
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
    out_path = join(settings.general['path'], 'EXE')
    in_path = settings.resources.get('frc_path', out_path)
    filename = splitext(filename)[0]
    return call([_getpath('frc.exe'),
                 "-c",
                 join(in_path, filename),
                 join(out_path, filename)
                ])


def extract_7z(source, dest):
    return call([_getpath('7z.exe'),
                 "x",
                 "%s.7z" % source,
                 "-o%s" % dest
                ])


def compile_7z(source, dest):
    return call([_getpath('7z.exe'),
                 "a",
                 "%s.7z" % dest,
                 source
                ])
