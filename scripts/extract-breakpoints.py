#!/usr/bin/env python3

import sys
from capstone import *
from capstone.x86 import *

breakpoints = set()

def is_conditional(id):
    return id in [X86_INS_JA, X86_INS_JAE, X86_INS_JBE, X86_INS_JB,
    X86_INS_JCXZ, X86_INS_JECXZ, X86_INS_JE, X86_INS_JGE, X86_INS_JG,
    X86_INS_JLE, X86_INS_JL, X86_INS_JNE,
    X86_INS_JNO, X86_INS_JNP, X86_INS_JNS, X86_INS_JO, X86_INS_JP,
    X86_INS_JRCXZ, X86_INS_JS]

with open(sys.argv[1], 'rb') as f:
    # offset .text section
    f.seek(0x80)
    buf = f.read()
    md = Cs(CS_ARCH_X86, CS_MODE_64)

    source = None
    target = None
    add_next = False
    for i in md.disasm(buf, 0x0):

        if add_next:
            # add address of instruction after cf that will be reached when
            # the jump was not taken
            breakpoints.add((source, target, i.address))
            add_next = False

        if is_conditional(i.id):
            # add address of cf instruction
            source = i.address

            # add target address of cf instruction when it is taken
            target = int(i.op_str, 16)

            # hint to add the address of the next instruction when jump is not taken
            add_next = True

with open(sys.argv[1] + '-breakpoints', 'w') as file:
    for source, target, not_taken in breakpoints:
        file.write('{},{},{}\n'.format(hex(source), hex(target), hex(not_taken)))
