#!/bin/python
"""
This script lets the user run a number of test cases against the assembler
"""

from mausembler import Assembler
import os

OPTIONS = {'stdlib_ilog': ('examples\\misc\\ilog.dasm',
                           'examples\\misc\\ilog.bin'),
         'simple_dependecy-test': ('examples\\includes\\part1.dasm',
                                   'examples\\includes\\part1+part2.bin'),
           "SirCmpwn's_test_case": ('examples\\misc\\.orgASM_test.dasm',
                           'examples\\misc\\.orgASM_test.bin'),
           "addition_test_case": ('examples\\math\\addition.dasm',
                           'examples\\math\\addition.bin')}


INST = Assembler()
INST.debug_toggle = True
print 'This performs a number of test cases on the assembler :D'
print "If you'll give me a moment, \
i'll clean up the .bin files from previous tests :)\n\n"

for test in range(len(OPTIONS)):
    cmd = ('del ' + OPTIONS[OPTIONS.keys()[test]][1])
    print cmd
    os.system(cmd)


print '\n\n0. All tests'
for test in range(len(OPTIONS)):
    print str(test + 1) + '.',
    print OPTIONS.keys()[test].replace('_', ' ')

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
