import re

#def s_ident(self, scanner, token): return token
#def s_operator(self, scanner, token): return "op%s" % token
#def s_float(self, scanner, token): return float(token)
#def s_int(self, scanner, token): return int(token)



class Sparser():
    def __init__(self, ):
        print 'Sparser; self-titled!'
    def parse(self, opcode):
        scanner = re.Scanner([
            (r"[a-zA-Z_]\w*", self.s_set),
            (r"\d+\.\d*", self.s_add),
            (r"\d+", self.s_sub),
            (r"=|\+|-|\*|/", self.s_mul),
            (r"\s+", self.s_div),
            ])

        #print scanner.scan("sum = 3*foo + 312.50 + bar")
        print 'Scanned:', scanner.scan(' '.join(opcode))

###########################################################
## here follows individual code for the different opcodes #
###########################################################
    def s_set(self, scanner, token):
        "0x1"
    def s_add(self, scanner, token):
        "0x2"
    def s_sub(self, scanner, token):
        "0x3"
    def s_mul(self, scanner, token):
        "0x4"
    def s_div(self, scanner, token):
        "0x5"
    def s_mod(self, scanner, token):
        "0x6"
    def s_shl(self, scanner, token):
        "0x7"
    def s_shr(self, scanner, token):
        "0x8"
    def s_and(self, scanner, token):
        "0x9"
    def s_bor(self, scanner, token):
        "0xa"
    def s_xor(self, scanner, token):
        "0xb"
    def s_ife(self, scanner, token):
        "0xc"
    def s_ifn(self, scanner, token):
        "0xd"
    def s_ifg(self, scanner, token):
        "0xe"
    def s_ivb(self, scanner, token):
        "0xf"