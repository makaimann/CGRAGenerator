#!/usr/bin/python

import os
import sys
import re
import random

# FIXME/TODO if tile 3 is memtile, use non-io templates etc.

# # OOPS with IO tiles included, first mem tile is...?  tile 14?
# # Replace 'DEPTH' with a decimal integer %03d
# MEM_TEMPLATE='''
#   #DELAY DEPTH,DEPTH
#   #
#   T14_mem_DEPTH # (fifo_depth=DEPTH)
#   self.in -> T14_in_s2t0 -> T14_mem_in
#   T14_mem_out -> T14_out_s2t0 -> self.out
# '''

# 8x8 grid w/ io pads
# Input from PE tile 11, output to mem tile T14
MEM_TEMPLATE='''
  #DELAY DEPTH,DEPTH
  #
  self.in -> T11_in_s2t0
  T11_in_s2t0 -> T11_out_s0t0
  T12_in_s2t0 -> T12_out_s0t0
  T13_in_s2t0 -> T13_out_s0t0
  T14_in_s2t0 -> T14_mem_in
  T14_mem_DEPTH # (fifo_depth=DEPTH)
  T14_mem_out -> T14_out_s1t1
  T14_in_s7t1 -> T14_out_s5t1 -> self.out
'''

# 16x16 grid w/ io pads
# Input must come in to T21_s2t0, output from T36_s0t0
# Input from PE tile 21 (0x15), output to mem tile T36 (0x24)
# PE: 21, 22, 23 MEM: 24
MEM_TEMPLATE='''
  #DELAY DEPTH,DEPTH
  #
  self.in -> T21_in_s2t0
  T21_in_s2t0 -> T21_out_s0t0
  T22_in_s2t0 -> T22_out_s0t0
  T23_in_s2t0 -> T23_out_s0t0
  T24_in_s2t0 -> T24_mem_in
  T24_mem_DEPTH # (fifo_depth=DEPTH)
  T24_mem_out -> T24_out_s0t0
  #
  T25_in_s2t0 -> T25_out_s0t0
  T26_in_s2t0 -> T26_out_s0t0
  T27_in_s2t0 -> T27_out_s0t0
  T28_in_s2t0 -> T28_out_s0t0
  #
  T29_in_s2t0 -> T29_out_s0t0
  T30_in_s2t0 -> T30_out_s0t0
  T31_in_s2t0 -> T31_out_s0t0
  T32_in_s2t0 -> T32_out_s0t0
  #
  T33_in_s2t0 -> T33_out_s0t0
  T34_in_s2t0 -> T34_out_s0t0
  T35_in_s2t0 -> T35_out_s0t0
  T36_in_s2t0 -> T36_out_s0t0 -> self.out
'''




# # Input from PE tile 11, output to PE tile T11
# MEM_TEMPLATE='''
#   #DELAY DEPTH,DEPTH
#   #
#   self.in -> T11_in_s2t0
#   T11_in_s2t0 -> T11_out_s0t0
#   T12_in_s2t0 -> T12_out_s0t0
#   T13_in_s2t0 -> T13_out_s0t0
#   T14_in_s2t0 -> T14_mem_in
#   T14_mem_DEPTH # (fifo_depth=DEPTH)
#   T14_mem_out -> T14_out_s2t1
#   T13_in_s0t1 -> T13_out_s2t1
#   T12_in_s0t1 -> T12_out_s2t1
#   T11_in_s0t1 -> T11_out_s2t1 -> self.out
# '''

# MEM_TEMPLATE='''
#   #DELAY DEPTH,DEPTH
#   #
#   self.in -> T11_in_s2t0 -> T11_out_s0t0 -> T12_out_s0t0 -> T13_out_s0t0
#   T14_in_s2t0 -> T14_mem_in
#   T14_mem_DEPTH # (fifo_depth=DEPTH)
#   T14_mem_out -> T14_out_s2t0 -> self.out
# '''

# Version for CGRA w/o IO tiles
# Replace 'DEPTH' with a decimal integer %03d
MEM_TEMPLATE_OLD='''
  #DELAY DEPTH,DEPTH
  #
  T3_mem_DEPTH # (fifo_depth=DEPTH)
  self.in -> T3_in_s2t0 -> T3_mem_in
  T3_mem_out -> T3_out_s2t0 -> self.out
'''

##############################################################################
# THIS ONE CRASHES!!
# OOPS with IO tiles included, first PE tile is...? tile 11?
# Replace OPNAME with name of operand e.g. 'add'
# BAD reg op1 ba
OP_TEMPLATE='''
  #DELAY 1,1
  #
  self.in -> T11_in_s2t0
  T11_in_s2t0 -> T11_op1 (r)
  T11_in_s2t0 -> T11_out_s1t0
  T11_out_s1t0 -> T11_op2
  T11_OPNAME(reg,wire)
  T11_pe_out -> T11_out_s0t1 -> self.out
'''

# OOPS with IO tiles included, first PE tile is...? tile 11?
# Replace OPNAME with name of operand e.g. 'add'
# GOOD reg op2 ab
OP_TEMPLATE='''
  #DELAY 1,1
  #
  self.in -> T11_in_s2t0
  T11_in_s2t0 -> T11_op1
  T11_in_s2t0 -> T11_out_s1t0
  T11_out_s1t0 -> T11_op2 (r)
  T11_OPNAME(wire,reg)
  T11_pe_out -> T11_out_s0t1 -> self.out
'''

# 8x8 grid w/ io tiles
# Input from PE tile 11, output to mem tile T14
OP_TEMPLATE='''
  #DELAY 1,1
  #
  self.in -> T11_in_s2t0
  T11_in_s2t0 -> T11_op1
  T11_in_s2t0 -> T11_out_s1t0
  T11_out_s1t0 -> T11_op2 (r)
  T11_OPNAME(wire,reg)
  T11_pe_out -> T11_out_s0t1
  T12_in_s2t1 -> T12_out_s0t1
  T13_in_s2t1 -> T13_out_s0t1
  T14_in_s2t1 -> T14_out_s1t1
  T14_in_s7t1 -> T14_out_s5t1 -> self.out
'''

# 16x16 grid w/ io pads
# Input must come in to T21_s2t0, output from T36_s0t0
# Input from PE tile 21 (0x15), output to mem tile T36 (0x24)
# PE: 21, 22, 23 MEM: 24
OP_TEMPLATE='''
  #DELAY 1,1
  #
  self.in -> T21_in_s2t0
  T21_in_s2t0 -> T21_op1
  T21_in_s2t0 -> T21_out_s1t0
  T21_out_s1t0 -> T21_op2 (r)
  T21_OPNAME(wire,reg)
  T21_pe_out -> T21_out_s0t0
  #
  T22_in_s2t0 -> T22_out_s0t0
  T23_in_s2t0 -> T23_out_s0t0
  T24_in_s2t0 -> T24_out_s0t0
  #
  T25_in_s2t0 -> T25_out_s0t0
  T26_in_s2t0 -> T26_out_s0t0
  T27_in_s2t0 -> T27_out_s0t0
  T28_in_s2t0 -> T28_out_s0t0
  #
  T29_in_s2t0 -> T29_out_s0t0
  T30_in_s2t0 -> T30_out_s0t0
  T31_in_s2t0 -> T31_out_s0t0
  T32_in_s2t0 -> T32_out_s0t0
  #
  T33_in_s2t0 -> T33_out_s0t0
  T34_in_s2t0 -> T34_out_s0t0
  T35_in_s2t0 -> T35_out_s0t0
  T36_in_s2t0 -> T36_out_s0t0 -> self.out
'''






# Version for CGRA w/o IO tiles
# Replace OPNAME with name of operand e.g. 'add'
OP_TEMPLATE_OLD='''
  #DELAY 1,1
  #
  self.in -> T0_in_s2t0
  T0_in_s2t0 -> T0_op1
  T0_in_s2t0 -> T0_out_s1t0
  T0_out_s1t0 -> T0_op2 (r)
  T0_OPNAME(wire,reg)
  T0_pe_out -> T0_out_s0t1 -> self.out
'''





# using get will return `None` if a key is not present rather than raise a `KeyError`
# print os.environ.get('KEY_THAT_MIGHT_EXIST')
# os.getenv is equivalent, and can also give a default value instead of `None`
# print os.getenv('KEY_THAT_MIGHT_EXIST', default_value)

if os.getenv('NO_IO_TILES'):
    MEM_TEMPLATE = MEM_TEMPLATE_OLD
    OP_TEMPLATE  =  OP_TEMPLATE_OLD


# # So what we gonna do is...
# # we gonna modify top_tb to send one-bit outputs
# # from pre-specified output wire like maybe "T4_out_s2t0.1",
# # to a separate output file something like CGRA_1bit.out
# 
# # Use PEs to process input pixel(s) for LUT
# # Use EQ function
# LUT_TEMPLATE='''
#   # Use EQ to turn 0/1 pixels and turn them into 0/1 bits on tracks 0,1,2
#   self.in -> T11_in_s2t0
#   T11_in_s2t0 -> T11_op1
#   T11_eq(const_1, wire)
#   T11_pe_out_res_p -> T11_out_s0t0.1
# 
#   T12_bit0 <- T12_in_s2t0
#   T12_bit3 <- T12_in_s2t0 (r)
#   T12_LUT(wire,const_0,reg) <- 0x01
#   T12_pe_out_res_p -> T12_out_s1t0.1
# '''
# 
# # Simple one to get us started
# LUT_TEMPLATE='''
#   T12_LUT(wire,const,reg) <- 0x01
#   T4_LUT <- 0xFF
#   T4_pe_out_res_p -> T4_out_s2t0.1
# '''

# NOPE start over
# * Set LUT registers for 3-input XOR maybe
# * If everything works right, a 0 pixel on the input should
#   translate to BUS1_S2_T0 single-bit signals on the first 3 PE tiles
# * Must route these to e.g. the three LUT inputs of the central PE
# * DON'T NEED/WANT EQ TRANSLATION!!! Ugh.
#
# 3-input AND looks like: 8'b10000000
# To load LUT with AND function: 0000TTTT 10000000
#
# Three LSB bits come in on e7, f5, 107 tracks 0,1,2 respectively

#  NOTE bit0<-S2 bit1<-S1, bit2<-S2


# 0 ...... ......  io1_02 io1_03 
# 1 ...... ......  io16_12 ......
# 2 io1_13 io16_14 pe_15  pe_16  
# 3 io1_27 ......  pe_28  pe_29  
# 4 io1_35 ......  pe_36  pe_37  
# 0 io1_47 ......  pe_48  pe_49  
# 1 io1_55 ......  pe_56  pe_57  
# 2 io1_67 ......  pe_68  pe_69  
# 3 io1_75 ......  pe_76  pe_77  
# 4 io1_87 ......  pe_88  pe_89  
# 0 io1_95 ......  pe_96  pe_97  
# 1 io1_A7 ......  pe_A8  pe_A9  
# 2 io1_B5 ......  pe_B6  pe_B7  
# 3 io1_C7 ......  pe_C8  pe_C9  
# 4 io1_D5 ......  pe_D6  pe_D7  
# 0 io1_E7 ......  pe_E8  pe_E9  
# 1 io1_F5 ......  pe_F6  pe_F7  
# 2 io1_107 ......  pe_108 pe_109 
#   ...... ......  io16_115 ......
#   ...... ......  io1_116 io1_117
#   
# 
# LUT_TEMPLATE='''
#   #DELAY 0,0
#   #
#   self.in ->  T0xE8_in_s2t0 ->  T0xE8_out_s1t0 -> T0xE8_bit2
#   self.in ->  T0xF6_in_s2t1 ->  T0xF6_out_s3t1 -> T0xE8_bit1
#   self.in -> T0x108_in_s2t2 -> T0x108_out_s3t2 -> T0xF6_out_s3t2 -> T0xE8_bit0
#   #
#   
# 
# 
# 
# 
#   self.in -> T21_in_s2t0
#   T21_in_s2t0 -> T21_op1
#   T21_in_s2t0 -> T21_out_s1t0
#   T21_out_s1t0 -> T21_op2 (r)
#   T21_OPNAME(wire,reg)
#   T21_pe_out -> T21_out_s0t0
#   #
#   T22_in_s2t0 -> T22_out_s0t0
#   T23_in_s2t0 -> T23_out_s0t0
#   T24_in_s2t0 -> T24_out_s0t0
#   #
#   T25_in_s2t0 -> T25_out_s0t0
#   T26_in_s2t0 -> T26_out_s0t0
#   T27_in_s2t0 -> T27_out_s0t0
#   T28_in_s2t0 -> T28_out_s0t0
#   #
#   T29_in_s2t0 -> T29_out_s0t0
#   T30_in_s2t0 -> T30_out_s0t0
#   T31_in_s2t0 -> T31_out_s0t0
#   T32_in_s2t0 -> T32_out_s0t0
#   #
#   T33_in_s2t0 -> T33_out_s0t0
#   T34_in_s2t0 -> T34_out_s0t0
#   T35_in_s2t0 -> T35_out_s0t0
#   T36_in_s2t0 -> T36_out_s0t0 -> self.out
# '''








# bsbuilder now has support for...
# op_data['add']     = 0x00000000
# op_data['sub']     = 0x00000001
# op_data['abs']     = 0x00000003
# op_data['gte']     = 0x00000004
# op_data['lte']     = 0x00000005
# op_data['eq']      = 0x00000006
# op_data['sel']     = 0x00000008
# op_data['rshft']   = 0x0000000F
# op_data['lshft']   = 0x00000011
# op_data['mul']     = 0x0000000B
# op_data['or']      = 0x00000012
# op_data['and']     = 0x00000013
# op_data['xor']     = 0x00000014

OP_LIST=[
    'add',
    'sub',
    'abs',
    'gte',
    'lte',
    'eq',
    'sel',
    'rshft',
    'lshft',
    'mul',
    'or',
    'and',
    'xor',
    ]

LBUF_LIST=[
    'lbuf10',
    'lbuf09'
    ]

DBG=0
VERBOSE = True

def main ():
    # For each test e.g. 'lbuf10' build bsb file 'lbuf10.bsb'
    # plus input and output files 'lbuf10_{input,output}.raw'

    if VERBOSE: print "gen_bsb_files.py:"

    # Run only specified tests, default to ALL tests
    tests = sys.argv[1:] # [0] is the command name
    if len(tests) == 0:      tests = OP_LIST+LBUF_LIST
    elif tests[0] == 'all':  tests = OP_LIST+LBUF_LIST
    elif tests[0] == '-all': tests = OP_LIST+LBUF_LIST

    # for testname in OP_LIST:   build_optest(testname)
    # for testname in LBUF_LIST: build_lbuftest(testname)

    for testname in tests:
        if testname in OP_LIST:   build_optest(testname)
        if testname in LBUF_LIST: build_lbuftest(testname)

def build_optest(testname):
    bsb = re.sub('OPNAME','%s' % testname, OP_TEMPLATE)
    write_bsb('op_' + testname, bsb, DBG=DBG)

def build_lbuftest(testname):
    delay = str(int(re.search('lbuf(\d+)', testname).group(1)))
    bsb = re.sub('DEPTH','%s' % delay, MEM_TEMPLATE)
    write_bsb('mem_' + testname, bsb, DBG=DBG)

def write_bsb(testname, bsb, DBG=1):
    # Remove excess indentation
    bsb = re.sub('\n\s+', '\n', bsb)

    # Add test name
    bsb = ('#TEST %s' % testname) + bsb
    if DBG: print bsb

    # ...and write the bsb file
    testfile = testname + '.bsb'
    outputstream = my_open(testfile, "w")
    outputstream.write(bsb)
    outputstream.close()
    if VERBOSE: print "  Built " + testfile

def my_open(filename, mode):
    no_overwrite = False
    if no_overwrite and os.path.exists(filename):
        sys.stderr.write("Don't wanna write over existing file '%s'" % filename)
        sys.exit(-1)
    return open(filename, mode)

main()

