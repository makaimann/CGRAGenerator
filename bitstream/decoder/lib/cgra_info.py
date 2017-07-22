#!/usr/bin/python

'''
To do this RIGHT...need to...
look in cgra_info for something like
    <sb feature_address='5' bus='BUS16'>
        <sel_width>2</sel_width>
        <mux snk='out_BUS16_S0_T0' reg='1' configh='1' configl='0' configr='40'>
          <src sel='0'>in_BUS16_S1_T0</src>
          <src sel='1'>in_BUS16_S2_T0</src>
          <src sel='2'>in_BUS16_S3_T0</src>
          <src sel='3'>pe_out_res</src>
        </mux>
...
decode_r0 would look for configbits between 0 and 31 
decode_r0 would look for configbits between 32 and 63
build a data structure maybe

  sb_connections_r0["0x3,3"] = ('out_BUS16_S0_T0','in_BUS16_S1_T0')
  sb_registers_r1["0x100"] = ('out_BUS16_S0_T0')


use the data structure like this sorta

  for (c in sb_connections_r0):
      parse = regexp("(.*),(.*)", c)
      mask = parse.group(1); val = parse.group(2)

'''
import re
import sys


# def sb_decode_cgra(bitstream_line):
#     '''
#     # Given a bitstream line e.g. "00050008 00000003",
#     # return FALSE if element is not a switchbox;
#     # otherwise return a connection dict and a reg list e.g.
#     #   connect["out_BUS16_S0_T0"] = "pe_out_res"
#     #   regs = ("out_BUS16_S0_T0", "out_BUS16_S1_T1")
#     '''
# 
#     regs = []
#     connections = {}
# 
#     # Address RREETTTT
#     f = re.search("(..)(..)(....) (........)", bitstream_line);
#     if (not f): return False;
# 
#     RR = f.group(1);       # register
#     EE = f.group(2);       # element
#     TTTT = f.group(3);     # tile
#     DDDDDDDD = f.group(4); # data
# 
# #     sb = get_switchbox(EE,TTTT)
# #     if (sb == False):
# #         # print "FOO not a switchbox"
# #         return (False,False)
# 
#     e = get_element(EE, TTTT)
#     if (e == False):      return (False, False)
#     elif (e.tag != 'sb'): return (False, False)
#     sb = e


# def sb_decode_cgra(sb,RR,DDDDDDDD):
def sb_decode(sb,RR,DDDDDDDD):
    '''
    # Given a pointer to a switchbox element in the xml,
    # return a connection dict and a reg list e.g.
    #   connections["out_BUS16_S0_T0"] = (1, 0, 3, "pe_out_res")
    #   regs = ("out_BUS16_S0_T0", "out_BUS16_S1_T1")
    '''
    DBG=0
    regs = []
    connections = {}

    if DBG: print "Found %s %s" % (sb.tag, str(sb.attrib))
    for mux in sb.iter('mux'):
        if DBG: print "  Found %s %s" % (mux.tag, str(mux.attrib))

        # Process the register
        # reg     = mux.attrib['reg']
        is_registered = False;
        if 'configr' in mux.attrib:
            configr = int(mux.attrib['configr'])
            regno = configr // 32
            regbit = configr % 32
            if DBG: print "    configr bit %3d = reg %d bit %2d" % (configr, regno, regbit)

            if regno != int(RR,16):
                if DBG: print "    wrong register\n"
            else:
                mask = 1 << regbit
                data = int(DDDDDDDD, 16)
                if (mask & data) != 0:
                    snk = mux.attrib['snk']
                    if DBG: print "*** Found registered output for '%s'" % snk
                    is_registered = True;
                    regs.append(snk)
                    if DBG: print "*** Now regs =", ; print regs
                    

        # Process the connection
        configh = int(mux.attrib['configh'])
        configl = int(mux.attrib['configl'])
        snk     = mux.attrib['snk']

        # Check to see if this is the right register
        regno  = configh // 32
        regbit = configh  % 32
        if DBG: print "    configh bit %2d = reg %d bit %2d" % (configh, regno, regbit)

        if regno != int(RR,16):
            if DBG: print "    wrong register"
        else:
            if DBG: print("    Found mux for output '%s'" % snk)
            field_width = configh - configl + 1
            field_mask  = 2**field_width - 1
            regbitl = (configl % 32)
            mask = field_mask << regbitl
            if DBG: print("    mux mask 0x%x = (0x%x << %d)" \
                          % (mask, field_mask, regbitl))

            data = int(DDDDDDDD, 16)
            if DBG: print("    data & mask = 0x%08x & 0x%08x = %08x"\
                          % (data, mask, data & mask))
            val = (data & mask) >> regbitl 
            if DBG: print("    val 0x%08x >> %d = %d"\
                          % (data & mask, regbitl, val))
            outwire = mux.attrib['snk']
            for src in mux:
                if DBG: print "      Found %s %s %s" % (src.tag, str(src.attrib), src.text)
                sel = int(src.attrib['sel'])
                if (sel == val):
                    inwire = src.text
                    if DBG: print "      ***Found inwire %s" % outwire
                    if DBG: print "      ***Found connection '%s' => '%s'" % (inwire, outwire)
                    connections[outwire] = (inwire,configh,configl,val)
                    if DBG: print "      ***Now connections =", ; print connections
                    
                    break
            if DBG: print "\n\n"
            
    return (regs, connections)



# global CGRA
global CGRA
CGRA = False
def read_cgra_info(filename):
    # https://docs.python.org/3/library/xml.etree.elementtree.html
    import xml.etree.ElementTree

    global CGRA
    CGRA = xml.etree.ElementTree.parse(filename).getroot()
    # print root
    # CGRA = root
    # return root


def tileno2rc(tileno):
    '''
    Search CGRA xml data structure with tile info e.g.
    <tile type='pe_tile_new' tile_addr='0' row='0' col='0' tracks='BUS1:5 BUS16:5 '>
    and return (row,col) corresponding to the given tile number.
    '''
    for tile in CGRA.iter('tile'):
        t = int(tile.attrib['tile_addr'])
        r = int(tile.attrib['row'])
        c = int(tile.attrib['col'])
        if t == tileno: return (r,c)
    print "ERROR Cannot find tile %d in cgra_info" % tileno

def rc2tileno(row,col):
    '''
    Search CGRA xml data structure with tile info e.g.
    <tile type='pe_tile_new' tile_addr='0' row='0' col='0' tracks='BUS1:5 BUS16:5 '>
    and return tile number corresponding to given (row,col)
    '''
    for tile in CGRA.iter('tile'):
        t = int(tile.attrib['tile_addr'])
        r = int(tile.attrib['row'])
        c = int(tile.attrib['col'])
        if (r,c) == (row,col): return t
    print "ERROR Cannot find tile corresponding to row %d col %d in cgra_info" \
          % (row,col)

def get_element(EE, TTTT):
    '''
    Retrieve the feature associated with element EE in tile TTTT.
    E.g. if EE="05" and TTTT="000C" returns f such that
    f.tag = "sb" etc.
    <sb feature_address='5' bus='BUS16'>
        <sel_width>2</sel_width>
        <mux snk='out_BUS16_S0_T0' reg='1' configh='1' configl='0' configr='40'>
          <src sel='0'>in_BUS16_S1_T0</src>
          <src sel='1'>in_BUS16_S2_T0</src>
    '''
    DBG=0
    global CGRA
    # if (CGRA == False): CGRA = read_cgra_info()
    if (CGRA == False):
        print "ERROR No CGRA data structure.  Did you call read_cgra_info()?"
        sys.exit(-1)

    tileno = int(TTTT,16)
    elemno = int(  EE,16)
    if DBG: print "Looking up tile %d element %d" % (tileno, elemno)
    for tile in CGRA.iter('tile'):
        t = int(tile.attrib['tile_addr'])
        r = int(tile.attrib['row'])
        c = int(tile.attrib['col'])
        if DBG: print "Found tile %2s (r%s c%s)" % (t, r, c)
        if (t == tileno):
            for feature in tile:
                if DBG: print "  Found feature %s" % feature.tag, ; print feature.attrib
                fa = int(feature.attrib['feature_address'])
                if (fa == elemno): return feature
    return False

# def get_switchbox(EE,TTTT):
#     '''
#     Given element EE (e.g. EE="05") in tile TTTT (e.g. TTTT="000C",
#     return False if element is not a switchbox;
#     else return the switchbox.
#     '''
#     e = get_element(EE, TTTT)
#     if e == False: return False;
#     else:          return e


# def get_switchbox(EE,TTTT):
#     '''
#     Given element EE (e.g. EE="05") in tile TTTT (e.g. TTTT="000C",
#     return False if element is not a switchbox;
#     else return the switchbox.
#     '''
#     DBG=0
#     global CGRA
#     if (CGRA == False): CGRA = read_cgra_info()
#     tileno = int(TTTT,16)
#     elemno = int(  EE,16)
#     print "FOO looking up tile %d element %d" % (tileno, elemno)
#     for tile in CGRA.iter('tile'):
#         t = int(tile.attrib['tile_addr'])
#         r = int(tile.attrib['row'])
#         c = int(tile.attrib['col'])
#         if DBG: print "Found tile %2s (r%s c%s)" % (t, r, c)
#         if (t == tileno):
#             for feature in tile:
#                 if DBG: print "  Found feature %s" % feature.tag, ; print feature.attrib
#                 fa = int(feature.attrib['feature_address'])
#                 if (fa == elemno):
#                     if (feature.tag == "sb"): return feature
#                     else: return False;
#     return False

def test():
#     # get_switchbox() test
#     sb = get_switchbox("05","0000")
#     if (sb != False):
#         print "Found switchbox %s %s" % (sb.tag, str(sb.attrib))

    # sb_decode() test
    sb_decode_cgra("00050008 00000003")

    # Should find a register here
    sb_decode_cgra("0105000E 00002000")

    # Maybe this will find two or three registers?  Looks like yes.
    sb_decode_cgra("0105000E 00007000")


    sys.exit(0)

# def read_cgra_info(filename):
#     DBG=9
#     # call(["ls", "-l", "examples"]) # exec/run/shell
#     if DBG: print "Using", filename, "as input";
# 
#     try:
#         inputstream = open(filename);
#     except IOError:
#         # TODO/FIXME yeah these were copies from somewhere else obviously
#         print ""
#         print "ERROR Cannot find processor bitstream file '%s'" % filename
#         print main.__doc__
#         sys.exit(-1);
# 
# 
#     # process_decoded_bitstream_old(inputstream)
#     for line in inputstream:
#         if (DBG>1): print line.rstrip()
#         line = line.strip() # why not
# 
# 
# 
# 
#     inputstream.close()
# 
# # read_cgra_info("examples/cgra_info.txt")
# 
#

# for configr in range(0,128):
#             regno = configr // 32
#             regbit = configr % 32
#             print "configr bit %3d = reg %d bit %2d" % (configr, regno, regbit)
#             if regbit == 31: print ""
#     # print "bit %d is in reg %d" % (b, b // 32)
# sys.exit(0)

