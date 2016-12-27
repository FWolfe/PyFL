# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 10:31:52 2016

@author: Fenris_Wolf
"""
import csv
from collections import namedtuple
from freelancer.core import tools, settings, log
_CACHE = { }
_REVERSE = {}

HashResult = namedtuple('HashResult', ('unsigned', 'signed', 'hex', 'text'))

def get_hash(text):
    return _CACHE.get(text.lower(), None)

def get_string(hash_id):
    return _REVERSE.get(int(hash_id), None)

def generate_cache(createid=True):
    if createid:
        output = tools.extract_hashes()
    else:
        with open(settings.general['hash_file']) as f:
            output = f.read().splitlines()

    csvr = csv.reader(output, delimiter=',', quotechar='"')
    for row in csvr:
            sign, text = row[0:2]
            sign = int(sign)
            unsign = int(sign & 0xffffffff)
            result = HashResult(unsign, sign, "0x%08x" % unsign, text)
            low_t = text.lower() 
            old = _CACHE.get(low_t) 
            if old:
                log.error("Hash Cache: overwritting cache for %s with %s" % (old, result))
            _CACHE[low_t] = result
            _REVERSE[sign] = result


def config():
    pass

