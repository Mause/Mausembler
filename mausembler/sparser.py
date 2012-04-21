#def s_ident(self, scanner, token): return token
#def s_operator(self, scanner, token): return "op%s" % token
#def s_float(self, scanner, token): return float(token)
#def s_int(self, scanner, token): return int(token)


class Sparser():
    def __init__(self, ):
        print 'Sparser; self-titled!'

    def parse(self, boss, opcode):
        data_word = ()
        output_data = []
        print '* '+str([x for x in opcode])
        if opcode[0] == 'SET':
            print "Line number:", boss.line_number#, '\nopcode:', opcode, '\ndata:', str(opcode[1])
            print '* set memory location', opcode[1], 'to', opcode[2]
            if opcode[2].upper() in boss.ops: value_proper = boss.ops[opcode[2]]
            elif opcode[2].upper() in boss.labels: value_proper = 'PASS'
            elif opcode[2].upper() in boss.registers: value_proper = boss.registers[opcode[2]]
            elif '[' in opcode[2] and opcode[2] not in boss.registers: print "You're pretty much screwed"; value_proper='PASS'
            else:
                try:
                    print '    * not working:',;
                    print opcode[2], ':', boss.ops[opcode[2].upper()];
                except KeyError:
                    print '\n    * definately not in there'
                value_proper = opcode[2]
                print '    * value_proper:', str(value_proper)
                print "    * boss's labels:", boss.labels
                if value_proper[0:2] != '0x':
                    try:
                        value_proper = hex(value_proper)
                    except TypeError:
                        print '    * already in hex'
                #print 'value_proper:', str(value_proper),
                print'\n'
                if len(value_proper) != 4:
                    try:
                        value_proper = int(value_proper)
                    except ValueError: pass
                    if type(value_proper) != int:
                        print 'value_proper:', str(value_proper), type(value_proper)
                        value_proper = (value_proper.split('x')[1]).rjust(4, '0')
            output_data = ['0x1f', (boss.registers[opcode[1].upper()]),
                                (boss.ops[opcode[0].upper()]), (value_proper)]

            data_word = (str(output_data[0].split('x')[1])+
                         str(output_data[1])+
                         str(output_data[2])+
                         str(output_data[3]))

            output_data.append(data_word)
            del value_proper

#        elif opcode[0] == 'ADD':
 #           print '* set', opcode[1], 'to', opcode[1], '+', opcode[2]
  #          boss.output_file.write(str(boss.ops[opcode[0]]))
   #     elif opcode[0] == 'SUB':
    #        print '* set', opcode[1], 'to', opcode[1], '-', opcode[2]
     #       boss.output_file.write(str(boss.ops[opcode[0]]))
      #  elif opcode[0] == 'MUL':
       #     print '* set', opcode[1], 'to', opcode[1], '*', opcode[2]
        #    boss.output_file.write(str(boss.ops[opcode[0]]))
#        elif opcode[0] == 'DIV':
 #           print '* set', opcode[1], 'to', opcode[1], '/', opcode[2]
  #          boss.output_file.write(str(boss.ops[opcode[0]]))
   #     elif opcode[0] == 'MOD':
    #        print '* set', opcode[1], 'to', opcode[1], '%', opcode[2]
     #       boss.output_file.write(str(boss.ops[opcode[0]]))

        #return output_data
        return data_word
#        scanner = re.Scanner([
 #           #(r"[a-zA-Z_]\w*", self.s_set),
  #          (r"[set]", self.s_set),
   #         (r"\d+\.\d*", self.s_add),
    #        (r"\d+", self.s_sub),
     #       (r"=|\+|-|\*|/", self.s_mul),
      #      (r"\s+", self.s_div),
       #     ])

#print 'output_data['+str(boss.line_number)+'] =', str(output_data)#[-1])
        #print scanner.scan("sum = 3*foo + 312.50 + bar")
        #print 'Scanned:', scanner.scan(' '.join(opcode))
