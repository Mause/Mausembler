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

print('0. All')
for index, test in enumerate(OPTIONS):
    print('{}. {}'.format(index + 1, test[0].replace('_', ' ')))


def get_test():
    test_num = input('Please enter a number: ')
    return int(test_num) if int(test_num) in range(0, len(OPTIONS) + 1) else get_test()

test_num = get_test()

import sys
if test_num == 0:
    for test_num in OPTIONS[1:]:
        sys.argv = [
            0,
            test_num[0],
            test_num[1]
        ]
        try:
            cli.main()
        except Exception as e:
            print(test_num[0], 'failed with {}: {}'.format(type(e), e))
else:
    sys.argv += [
        OPTIONS[test_num - 1][1],
        'null.bin'
    ]
    cli.main()
