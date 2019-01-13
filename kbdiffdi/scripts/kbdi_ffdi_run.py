#!/usr/bin/env python

import argparse
import time
import os

from kbdiffdi import *

def __parse_args():
    parser = argparse.ArgumentParser(description="""Script for computing kbdi and ffdi
                                                    """)

    parser.add_argument('-i',
                        '--input filename',
                        dest='input_filename',
                        required=True,
                        type=str)
    parser.add_argument('-o',
                        '--output filename',
                        dest='output_filename',
                        required=True,
                        type=str)
    parser.add_argument('-v',
                        '--verbose',
                        dest='verbose',
                        action='store_true',
                        default=True)
    args = parser.parse_args()

    if args.verbose:
        print("------------ User Input ----------------")
        print('input file:\t' + args.input_filename)
        print('output file:\t' + args.output_filename)
        print()

    return args

def __check_args(args):
    args_are_good = True
    
    if not os.path.exists(args.input_filename):
        print("[ERROR] - input file: " + args.input_filename + " doesn't exist")
        print(" ... check to make sure the filename and filepath are correct")
        print()
        args_are_good = False

    if not os.path.exists(os.path.dirname(args.output_filename)):
        print("[ERROR] - output filepath: " + os.path.dirname(args.output_filename) + " doesn't exist")
        print(" ... you tried to save the output file to a directory that doesn't exist. \n check to make sure the filepath is set correctly")
        print()
        args_are_good = False

    if not args_are_good:
        print(" ------- PROGRAM FAILED :( -------")

    return args_are_good

def run_kbdi_ffdi(input_filename, output_filename):
    print('[INFO] reading input')
    rain, temp, relhum, wind = input_output.load_csv(input_filename)
    
    print("[INFO] computing KBDI")
    kbdi = indices.KBDI()
    out_kbdi = kbdi.fit(temp, rain)
    
    print("[INFO] computing FFDI")
    ffdi = indices.FFDI()
    out_ffdi, out_df = ffdi.fit(out_kbdi, rain, temp, wind, relhum)

    print("[INFO] writing output to .csv")
    input_output.write_csv(input_filename, output_filename, out_kbdi, out_ffdi, out_df)


def main():
    print("\n\
 _   ______________ _____     __________________ _____ \n\
| | / /| ___ \  _  \_   _|    |  ___|  ___|  _  \_   _|\n\
| |/ / | |_/ / | | | | |______| |_  | |_  | | | | | |  \n\
|    \ | ___ \ | | | | |______|  _| |  _| | | | | | |  \n\
| |\  \| |_/ / |/ / _| |_     | |   | |   | |/ / _| |_ \n\
\_| \_/\____/|___/  \___/     \_|   \_|   |___/  \___/ \n\
                                                       ")
    start_time = time.time()
    print('\nStart date & time --- (%s)\n' % time.asctime(time.localtime(time.time())))

    args = __parse_args()

    if __check_args(args):
        run_kbdi_ffdi(args.input_filename, args.output_filename)

    tot_sec = time.time() - start_time
    minutes = int(tot_sec // 60)
    sec = tot_sec % 60
    print('\nEnd data & time -- (%s)\nTotal run-time -- (%d min %f sec)\n' %
        (time.asctime(time.localtime(time.time())), minutes, sec))

if __name__ == "__main__":
    main()
