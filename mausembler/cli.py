import os
import logging
import argparse
from .assembler import Assembler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument("input_filename")
    parser.add_argument("output_filename")
    parser.add_argument("--credits", help="prints credits and exits", action="store_true")
    parser.add_argument("--big-endian", help="enables big endian. defaults to little")
    parser.add_argument("-v", "--verbose", help="increases verbosity", action="count")
    args = parser.parse_args()

    if args.credits:
        print('First, notch! Cheers matey!')
        print('Secondly, startling! For answering my questions!')
        print('And thirdly, me. For writing the code')
    else:
        # calculate verbosity
        if args.verbose == 1:
            verbosity = logging.INFO
        elif args.verbose == 2:
            verbosity = logging.DEBUG
        else:
            verbosity = None

        input_filename = os.path.abspath(args.input_filename)
        output_filename = os.path.abspath(args.output_filename)

        state = {
            'input_directory': os.path.abspath(os.path.dirname(input_filename))
        }
        endianness = 'big' if args.big_endian else 'little'
        asm = Assembler(
            state=state,
            verbosity=verbosity,
            endianness=endianness)

        with open(input_filename) as file_handle:
            raw_assembly = file_handle.readlines()

        byte_code = asm.assemble(raw_assembly)

        with open(output_filename, 'wb') as fh:
            fh.write(byte_code)

        asm.log_file.info('Done')

if __name__ == '__main__':
    main()
