#!/bin/bash

# SR Yes, I know, the name of this script is "run.csh"
# but it's written in bash instead of csh :(


# @Caleb: For providing registers on all outputs of all SBs, do-
# setenv CGRA_GEN_ALL_REG 1 (csh syntax)
# export CGRA_GEN_ALL_REG=1  (sh syntax)
export CGRA_GEN_ALL_REG=1


if [ -d genesis_verif ]; then
  rm -rf genesis_verif
fi

# SR 3/29
# If using verilator, change inouts to separate ins and outs (part 1)
# i.e. use ../io1bit/verilator_hack/io1bit.vp instead of ../io1bit/io1bit.vp
#
./fix_inouts.csh io1bit | sed '$d'
if [[ `./fix_inouts.csh io1bit` == "NO_VHACK" ]]; then
  echo '  Note: not using verilator tri/inout hack';
  io1bit=../io1bit/io1bit.vp;
else
  echo "  Verilator hack part 1 (pre-genesis): use verilator_hack/io1bit.vp instead";
  io1bit=../io1bit/verilator_hack/io1bit.vp;
fi


Genesis2.pl -parse -generate -top top -hierarchy top.xml -input\
  top.vp \
  \
  ../sb/sb.vp \
  ../cb/cb.vp \
  \
  ../pe_new/pe/rtl/test_pe_red.svp \
  ../pe_new/pe/rtl/test_pe_dual.vpf \
  ../pe_new/pe/rtl/test_pe_comp.svp \
  ../pe_new/pe/rtl/test_pe_comp_dual.svp \
  ../pe_new/pe/rtl/test_cmpr.svp \
  ../pe_new/pe/rtl/test_pe.svp \
  ../pe_new/pe/rtl/test_mult_add.svp \
  ../pe_new/pe/rtl/test_full_add.svp \
  ../pe_new/pe/rtl/test_lut.svp      \
  ../pe_new/pe/rtl/test_opt_reg.svp  \
  ../pe_new/pe/rtl/test_simple_shift.svp \
  ../pe_new/pe/rtl/test_shifter.svp  \
  ../pe_new/pe/rtl/test_debug_reg.svp  \
  ../pe_new/pe/rtl/test_opt_reg_file.svp  \
  \
  ../pe_tile_new/pe_tile_new.vp \
  \
  ../empty/empty.vp \
  $io1bit \
  ../io16bit/io16bit.vp \
  ../global_signal_tile/global_signal_tile.vp \
  \
  ../memory_tile/memory_tile.vp \
  ../memory_core/input_sr.vp \
  ../memory_core/output_sr.vp \
  ../memory_core/linebuffer_control.vp \
  ../memory_core/fifo_control.vp \
  ../memory_core/mem.vp \
  ../memory_core/memory_core.vp \
  \
  ../global_controller/global_controller.svp \
  \
  ../jtag/jtag.svp \
  ../jtag/Template/src/digital/template_ifc.svp \
  ../jtag/Template/src/digital/cfg_ifc.svp \
  ../jtag/Template/src/digital/flop.svp \
  ../jtag/Template/src/digital/tap.svp \
  ../jtag/Template/src/digital/reg_file.svp \
  ../jtag/Template/src/digital/cfg_and_dbg.svp \
  || exit 13



# echo
# echo HACKWARNING Restoring original LUT code
# echo HACKWARNING Restoring original LUT code
# echo HACKWARNING Restoring original LUT code
# echo git checkout ../pe_new/pe/rtl/test_pe.svp
# git checkout ../pe_new/pe/rtl/test_pe.svp
# echo


echo
echo HACKWARNING Using custom stub instead of proprietary DW_tap
echo HACKWARNING Using custom stub instead of proprietary DW_tap
echo HACKWARNING Using custom stub instead of proprietary DW_tap
echo cp  ../jtag/Template/src/digital/DW_tap.v.stub genesis_verif/DW_tap.v
cp  ../jtag/Template/src/digital/DW_tap.v.stub genesis_verif/DW_tap.v
ls -l ../jtag/Template/src/digital/DW_tap.v.stub
ls -l genesis_verif/DW_tap.v
echo

# What are these?  Why are they here?
source clean_up_cgra_inputs.csh
source remove_genesis_wires.csh

# SR 3/29
# If using verilator, change inouts to separate ins and outs (part 2)
# See 'fix_inouts.csh' code for details
./fix_inouts.csh top


# Fixed now maybe
# # Must fix e.g.  <depth bith='15' bitl='3'>0</depth>
# # should be <fifo_depth bith='15' bitl='3'>0</fifo_depth>
# # Second run below should say 'no errors found'
# ./find_and_fix_depth_problems.csh
# ./find_and_fix_depth_problems.csh


# SR 3/29 looks like this got fixed maybe?
# # Must fix e.g.
# #       <src sel='0'>in_1_BUS16_0_3</src>
# # should be
# #       <src sel='0'>in_1_BUS16_S0_T3</src>
# # 
# ./find_and_fix_ST_deficient_memwires.csh
# ./find_and_fix_ST_deficient_memwires.csh


if [ `hostname` == "kiwi" ]; then
  echo Checking cgra_info for errors...
  echo xmllint --noout cgra_info.txt
  xmllint --noout cgra_info.txt 2>&1 | head -n 20
fi
