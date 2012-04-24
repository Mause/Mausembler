#!/bin/python
from mausembler import Assembler

options = {'stdlib_ilog': ('examples\\misc\\ilog.dasm',
                           'examples\\misc\\ilog.bin'),
         'simple_dependecy-test': ('examples\\includes\\part1.dasm',
                                   'examples\\includes\\part1+part2.bin')}

inst = Assembler()

print 'This performs a number of test cases on the assembler :D'
print "If you'll give me a moment, ill clean up the .bin files from previous tests :)\n"

print '0. All tests'
for test in range(len(options)):
    print str(test+1)+'.', options.keys()[test].replace('_', ' ')

print #range(len(options)+1)
test_num = raw_input('Please enter a number: ')
possibles = [str(x) for x in range(len(options)+1)]
while test_num not in possibles:
    test_num = raw_input('Please enter a number: ')
    if test_num not in possibles:
        print 'Sorry, please try again\n'

test_num = int(test_num)

print 

#print options[options.keys()[test_num-1]]#[0], options[options.keys()[test_num]][1])

if test_num != 0:
    input_filename = options[options.keys()[test_num-1]][0]
    output_filename = options[options.keys()[test_num-1]][1]
    inst.load(input_filename, output_filename)
else:
    print 'Tobe implemented'


print 'Test done'