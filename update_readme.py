#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import hashlib


class InvalidFileFormatException(Exception):
    pass


def load_signed():
    signed_set  = set() # a set of tuples: ( name, other_info )

    # "name | position"
    sig_pattern_1 = r""" ([^|]+)    # name 
                         \|         # separator
                         ([^|]+)    # company, position etc
                     """

    # "| name | position |"
    sig_pattern_2 = r""" \|         # left-sep
                         ([^|]+)    # name 
                         \|         # middle-separator
                         ([^|]+)    # company, position etc
                         \|         # right-sep
                     """

    pattern1 = re.compile( sig_pattern_1, re.VERBOSE )
    pattern2 = re.compile( sig_pattern_2, re.VERBOSE )


    dir = 'signed'
    for basename in os.listdir(dir):
        filename = os.path.join(dir, basename)
        if not os.path.isfile(filename):
            print('Skipping non-file "%s"' % filename)
            continue

        with open(filename) as inp:
            for i, line in enumerate(inp):
                line = line.strip()
                if not line:
                    continue

                m = re.match(pattern1, line) or re.match(pattern2, line)                
                if not m :
                    raise InvalidFileFormatException(
                        'File "%s", line %d: line does not follow the format:\n\t"%s"'
                        % (filename, i + 1, line)
                    )

                signed_set.add((m.group(1).strip(), m.group(2).strip()))

    signed_list = sorted(signed_set, key=lambda pair: hashlib.sha256(repr(pair).encode('utf-8')).hexdigest())    
    return signed_list


def write_signed(signed, outp):
    for i, signature in enumerate(signed):
        outp.write('| {:<4} | {:<34} | {:<39} |\n'.format(i+1, signature[0], signature[1]))


def update_readme(signed):
    with open('pre-readme.md') as inp, open('README.md', 'w') as outp:
        for line in inp:
            if line.strip() == '<!-- Signed -->':
                write_signed(signed, outp)
            else:
                outp.write(line)


def main():
    signed = load_signed()
    update_readme(signed)


if __name__ == '__main__':
    main()