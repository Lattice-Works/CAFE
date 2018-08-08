#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser
from chroniclepy import preprocessing

def get_parser():
    parser = ArgumentParser(description = 'ChroniclePy: Preprocessing and Summarizing Chronicle data')
    parser.add_argument('stage', choices=['preprocessing'],
        help = 'processing stage to be run: preprocessing or summary')
    parser.add_argument('input_dir', action='store',
        help = 'the folder with data files (csv\'s).')
    parser.add_argument('output_dir', action='store',
        help = 'the folder to write output files.')

    prepargs = parser.add_argument_group('Options for preprocessing the data.')
    prepargs.add_argument('--recodefile',action='store', default=None,
        help = 'a csv file with one column named "fullname" \
            with transformations of the apps (eg. category codes, other names,...)')
    prepargs.add_argument('--precision',action='store',type=int, default = 3600,
        help = 'the precision in seconds for the output file. This defines the time \
            unit of the data.  Eg. if the data should be split up by the hour, use 3600.')
    prepargs.add_argument('--sessioninterval', action='store',type=int, default = 60*10,
        help = 'the interval (in seconds) that define the start of a new session, i.e. \
            how long should the break be between 2 sessions of phone usages to be considered \
            a new session.')
    return parser

def main():
    opts = get_parser().parse_args()

    if opts.stage=='preprocessing':
        preprocessing.preprocess(
            infolder = opts.input_dir,
            outfolder = opts.output_dir,
            recodefile = opts.recodefile,
            precision = opts.precision,
            sessioninterval = opts.sessioninterval
            )

if __name__ == '__main__':
    main()
