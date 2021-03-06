basic_opcodes = {
    'SET': 0x01, 'ADD': 0x02, 'SUB': 0x03,
    'MUL': 0x04, 'MLI': 0x05, 'DIV': 0x06,
    'DVI': 0x07, 'MOD': 0x08, 'MDI': 0x09,
    'AND': 0x0a, 'BOR': 0x0b, 'XOR': 0x0c,
    'SHR': 0x0d, 'ASR': 0x0e, 'SHL': 0x0f,
    'IFB': 0x10, 'IFC': 0x11, 'IFE': 0x12,
    'IFN': 0x13, 'IFG': 0x14, 'IFA': 0x15,
    'IFL': 0x16, 'IFU': 0x17, 'NOP': 0x18,
    'NOP': 0x19, 'ADX': 0x1a, 'SBX': 0x1b,
    'NOP': 0x1c, 'NOP': 0x1d, 'STI': 0x1e,
    'STD': 0x1f
}

special_opcodes = {
    'NOP': 0x00, 'JSR': 0x01, 'NOP': 0x02, 'NOP': 0x03,
    'NOP': 0x04, 'NOP': 0x05, 'NOP': 0x06, 'HCF': 0x07,
    'INT': 0x08, 'IAG': 0x09, 'IAS': 0x0a, 'IAP': 0x0b,
    'NOP': 0x0c, 'NOP': 0x0d, 'NOP': 0x0e, 'NOP': 0x0f,
    'HWN': 0x10, 'HQN': 0x11, 'HWI': 0x12, 'NOP': 0x13,
    'NOP': 0x14, 'NOP': 0x15, 'NOP': 0x16, 'NOP': 0x17,
    'NOP': 0x18, 'NOP': 0x19, 'NOP': 0x1a, 'NOP': 0x1b,
    'NOP': 0x1c, 'NOP': 0x1d, 'NOP': 0x1e, 'NOP': 0x1f
}

values = {
    'A': 0x00, 'B': 0x01,
    'C': 0x02, 'X': 0x03,
    'Y': 0x04, 'Z': 0x05,
    'I': 0x06, 'J': 0x07,
    '[A]': 0x08, '[B]': 0x09,
    '[C]': 0x0a, '[X]': 0x0b,
    '[Y]': 0x0c, '[Z]': 0x0d,
    '[I]': 0x0e, '[J]': 0x0f,
    # 0x10-0x17: [next word + register] goes here
    'POP': 0x18, '[SP++]': 0x18,
    'PUSH': 0x18, '[--SP': 0x18,
    'PEEK': 0x19, '[SP]': 0x19,
    '[SP+[PC++]]': 0x1a, '[--SP]': 0x1a,
    'SP': 0x1b, 'PC': 0x1c,
    'EX': 0x1d, '[PC++]': 0x1e,
    'PC++': 0x1f,
}
