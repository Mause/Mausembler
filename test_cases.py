#!/bin/python3
import os
# import unittest
from mausembler import cli


OPTIONS = [
    ('stdlib_ilog', 'examples/misc/ilog.dasm'),
    ('simple_dependecy-test', 'examples/includes/part1.dasm'),
    ("SirCmpwn's_test_case", 'examples/misc/.orgASM_test.dasm'),
    ("addition_test_case", 'examples/math/addition.dasm'),
    ("math_test_case", 'examples/math/basic_commands.dasm'),
    ("sixteens_draw_test", 'examples/sixteens/draw.asm'),
    ("sixteens_quick_example", 'examples/sixteens/quick_example.asm'),
    ("sixteens_refresh_test", 'examples/sixteens/refresh.asm'),
    ("sixteens_vram_test", 'examples/sixteens/vram.asm')
]


#INST.debug_toggle = True #  debugging line. enable to know ALL the stuffs :D
print('This performs a number of test cases on the assembler :D')
print("If you'll give me a moment, i'll clean up the .bin files from previous tests :)")

try:
    os.remove(os.path.join(os.getcwd(), 'null.bin'))
except (WindowsError, OSError):
    pass  # ok, that file doesnt exist

for index, test in enumerate(OPTIONS):
    print('{}. {}'.format(index + 1, test[0].replace('_', ' ')))


def get_test():
    TEST_NUM = input('Please enter a number: ')
    return int(TEST_NUM) if int(TEST_NUM) in range(1, len(OPTIONS) + 1) else get_test()

TEST_NUM = get_test() - 1

print(OPTIONS[TEST_NUM - 1][1])

# if TEST_NUM == 0:
#     for TEST_NUM in POSSIBLES[1:]:
#         TEST_NUM = int(TEST_NUM)
#         INPUT_FILENAME = OPTIONS[OPTIONS[TEST_NUM - 1]][0]
#         OUTPUT_FILENAME = OPTIONS[OPTIONS[TEST_NUM - 1]][1]
#         INST.load(INPUT_FILENAME, OUTPUT_FILENAME)
# else:

import sys
sys.argv += [
    OPTIONS[TEST_NUM - 1][1],
    'null.bin'
]
cli.main()
