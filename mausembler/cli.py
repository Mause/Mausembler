import os
from .assembler import Assembler


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename")
    parser.add_argument("output_filename")
    parser.add_argument("--credits", help="prints credits and exits")
    parser.add_argument("--big-endian", help="enables big endian. defaults to little")
    parser.add_argument(
        "-d", "--debug", help="enable debug mode", action="store_true")
    args = parser.parse_args()

    if args.credits:
        print('First, notch! Cheers matey!')
        print('Secondly, startling! For answering my questions!')
        print('And thirdly, me. For writing the code')
    else:
        input_filename = os.path.abspath(args.input_filename)
        output_filename = os.path.abspath(args.output_filename)

        state = {
            'input_directory': os.path.abspath(os.path.dirname(input_filename))
        }
        asm = Assembler(state)

        asm.debug_toggle = args.debug
        asm.endian = 'big' if args.big_endian else 'little'

        with open(input_filename) as file_handle:
            raw_assembly = file_handle.readlines()

        byte_code = asm.assemble(raw_assembly)

        with open(output_filename, 'wb') as fh:
            fh.write(byte_code)


if __name__ == '__main__':
    main()
