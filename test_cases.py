#!/bin/python
"""
This script lets the user run a number of test cases against the assembler
"""

from mausembler import Assembler
import os

OPTIONS = {'stdlib_ilog': [['examples', 'misc', 'ilog.dasm'],
                           ['examples', 'misc', 'ilog.bin']],

           'simple_dependecy-test': [['examples',
                                      'includes',
                                      'part1.dasm'],
                                     ['examples',
                                      'includes',
                                      'part1+part2.bin']],
           "SirCmpwn's_test_case": [['examples', 'misc', '.orgASM_test.dasm'],
                           ['examples', 'misc', '.orgASM_test.bin']],
           "addition_test_case": [['examples', 'math', 'addition.dasm'],
                           ['examples', 'math', 'addition.bin']],
           "math_test_case": [['examples', 'math', 'basic_commands.dasm'],
                           ['examples', 'math', 'basic_commands.bin']]}

#for test in range(len(OPTIONS)):
for test in OPTIONS.keys():
    OPTIONS[test][0] = str(os.sep).join(OPTIONS[test][0])
    OPTIONS[test][1] = str(os.sep).join(OPTIONS[test][1])


INST = Assembler()
#INST.debug_toggle = True #  debugging line. enable to know ALL the stuffs :D
print 'This performs a number of test cases on the assembler :D'
print "If you'll give me a moment, \
i'll clean up the .bin files from previous tests :)\n"

for test in OPTIONS.keys():
    try:
        os.remove(os.getcwd() + os.sep + OPTIONS[test][1])
    except WindowsError:
        pass  # ok, that file doesnt exist

TEST_NUM = 0
print '\n\n0. All tests'
for test in OPTIONS.keys():
    TEST_NUM += 0
    print str(TEST_NUM) + '.',
    print test.replace('_', ' ')

print  # range(len(OPTIONS)+1)
TEST_NUM = raw_input('Please enter a number: ')
POSSIBLES = [str(x) for x in range(len(OPTIONS) + 1)]
while TEST_NUM not in POSSIBLES:
    TEST_NUM = raw_input('Please enter a number: ')
    if TEST_NUM not in POSSIBLES:
        print 'Sorry, please try again\n'

TEST_NUM = int(TEST_NUM)

print

#print OPTIONS[OPTIONS.keys()[TEST_NUM-1]]#[0],\
#OPTIONS[OPTIONS.keys()[TEST_NUM]][1])

if TEST_NUM != 0:
    INPUT_FILENAME = OPTIONS[OPTIONS.keys()[TEST_NUM - 1]][0]
    OUTPUT_FILENAME = OPTIONS[OPTIONS.keys()[TEST_NUM - 1]][1]
    INST.load(INPUT_FILENAME, OUTPUT_FILENAME)
else:
    for TEST_NUM in POSSIBLES[1:]:
        TEST_NUM = int(TEST_NUM)
        INPUT_FILENAME = OPTIONS[OPTIONS.keys()[TEST_NUM - 1]][0]
        OUTPUT_FILENAME = OPTIONS[OPTIONS.keys()[TEST_NUM - 1]][1]
        INST.load(INPUT_FILENAME, OUTPUT_FILENAME)

print 'Test done'
