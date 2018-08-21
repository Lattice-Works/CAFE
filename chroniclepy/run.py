#!/usr/bin/python

from argparse import ArgumentParser
from chroniclepy import preprocessing, summarising
import os

def get_parser():
    parser = ArgumentParser(description = 'ChroniclePy: Preprocessing and Summarizing Chronicle data')
    parser.add_argument('stage', choices=['preprocessing','summary','all'],
        help = 'processing stage to be run: preprocessing or summary')
    parser.add_argument('input_dir', action='store',
        help = 'the folder with data files (csv\'s).')
    parser.add_argument('preproc_dir', action='store',
        help = 'the folder to write preprocessed files.')
    parser.add_argument('output_dir', action='store',
        help = 'the folder to write output files.')


    prepargs = parser.add_argument_group('Options for preprocessing the data.')
    prepargs.add_argument('--precision',action='store',type=int, default = 3600,
        help = 'the precision in seconds for the output file. This defines the time \
            unit of the data.  Eg. if the data should be split up by the hour, use 3600.')
    prepargs.add_argument('--sessioninterval', action='append', default=['60'],
        help = 'the interval (in seconds) that define the start of a new session, i.e. \
            how long should the break be between 2 sessions of phone usages to be considered \
            a new session.')

    summaryargs = parser.add_argument_group('Options for summarising the data.')
    summaryargs.add_argument('--recodefile',action='store', default=None,
        help = 'a csv file with one column named "fullname" \
        with transformations of the apps (eg. category codes, other names,...)')
    summaryargs.add_argument('--includestartend', action='store_true', default=False,
        help = 'flag to include the first and last day in the summary table.')
    return parser

def main():
    opts = get_parser().parse_args()

    if opts.stage=='preprocessing' or opts.stage=='all':
        preprocessing.preprocess(
            infolder = opts.input_dir,
            outfolder = opts.preproc_dir,
            precision = opts.precision,
            sessioninterval = [int(x) for x in opts.sessioninterval]
            )

    if opts.stage=='summary' or opts.stage=='all':
        summarising.summary(
            infolder = opts.preproc_dir,
            outfolder = opts.output_dir,
            includestartend = opts.includestartend,
            recodefile = opts.recodefile
        )

if __name__ == '__main__':
    main()
