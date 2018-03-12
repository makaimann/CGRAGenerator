#!/bin/csh -f

# USAGE: $0 <-v|-q> <testbench> <tracefile>

unset VERBOSE
if ("$1" == "-v") then
  set VERBOSE; shift
endif

if ("$1" == "-q") then
  unset VERBOSE; shift
endif

set testbench = $1
echo $#argv
unset tracefile
if ($#argv == 2) set tracefile = $2

  # Build the necessary switches

  # Gather the verilog files for verilator command line
  set vdir = ../../hardware/generator_z/top/genesis_verif
  pushd $vdir >& /dev/null
    # set vfiles = (*.v *.sv)
    set vfiles = (*.v)
  popd >& /dev/null

  # So many warnings it wants to DIE!
  set myswitches = '-Wno-fatal'
  set top        = 'top'

  # Add trace switch if trace requested
  if ($?tracefile) set myswitches = "$myswitches --trace"

  # Note default trace_filename in top_tb.cpp is "top_tb.vcd"

  # Run verilator to build the simulator.

  # build C++ project

  set opt = ''

# Hey HEY built a test_pe that maybe has working LUTs for kiwi;
# new LUT code gets swapped in by top/run.csh
#
#   ########################################################################
#   # O0 hack for nbdev3 and beyond: only runs on kiwi if opt OFF
# 
#   set opt = ''
#   set branch = `git rev-parse --abbrev-ref HEAD`
#   set badbranch = nbdev3
#   if (! $?TRAVIS && "$branch" == "$badbranch") then
# 
#     # OMG -O0 is SOO SLOWWW let's just disable luts instead
#     # set opt = '-O0'
#     # echo
#     # echo "WARNING VERILATOR OPT LEVEL 0 (NO OPT)"
#     # echo "WARNING VERILATOR OPT LEVEL 0 (NO OPT)"
#     # echo "WARNING VERILATOR OPT LEVEL 0 (NO OPT)"
# 
#     set hwdir = $vdir/../..
#     echo "WARNING LUTS (and res_p) DISABLED b/c kiwi + $badbranch"
#     echo "WARNING LUTS (and res_p) DISABLED b/c kiwi + $badbranch"
#     echo "WARNING LUTS (and res_p) DISABLED b/c kiwi + $badbranch"
#     echo
#     echo diff $vdir/test_pe_unq1.sv $hwdir/pe_new/pe/rtl/test_pe_unq1.sv.no_lut
#     diff $vdir/test_pe_unq1.sv $hwdir/pe_new/pe/rtl/test_pe_unq1.sv.no_lut
# #     echo
# #     echo cp $hwdir/pe_new/pe/rtl/test_pe_unq1.sv.no_lut $vdir/test_pe_unq1.sv
# #     cp $hwdir/pe_new/pe/rtl/test_pe_unq1.sv.no_lut $vdir/test_pe_unq1.sv || exit 13
# 
#   endif

  set tmpdir = `mktemp -d /tmp/build_verilator.XXX`

  echo
  echo verilator $opt -Wall $myswitches --cc --exe $testbench \
    -y $vdir $vfiles --top-module $top \
    | fold -s | sed '2,$s/^/  /' | sed 's/$/  \\/'
  echo

  # verilator --version; g++ --version

  verilator $opt $myswitches -Wall $myswitches --cc --exe $testbench \
    -y $vdir $vfiles --top-module $top \
    >& $tmpdir/verilator.out

  set verilator_exit_status = $status

  if ($?VERBOSE) then
    echo "%Warning1 Ignoring warnings about unoptimizable circularities in switchbox wires (see SR for explainer)."
    echo '%Warning2 To get the flavor of all the warnings, just showing first 40 lines of output.'
    echo "%Warning3 See $tmpdir/verilator.out for full log."
    echo

    # This (head -n 40) can cause broken pipe error (!)
    # awk -f ./run-verilator-warning-filter.awk $tmpdir/verilator.out | head -n 40
    awk -f ./run-verilator-warning-filter.awk $tmpdir/verilator.out

  else
    echo "See $tmpdir/verilator.out for full log of verilator warnings."
  endif

  if ($verilator_exit_status != 0) then
    tail -40 $tmpdir/verilator.out
    echo ""
    echo "VERILATOR FAILED!"
    echo "See $tmpdir/verilator.out for full log of verilator warnings."
    exit -1
  endif

  echo
  echo "build_simulator.csh: Build the testbench..."

  set vtop = 'Vtop'
  if ($?VERBOSE) then
    echo
    echo "make \"
    echo "  -j -C obj_dir/ -f $vtop.mk $vtop"
  endif

  echo
  if (-e obj_dir/Vtop) /bin/rm obj_dir/Vtop

  echo "make $vtop -j -C obj_dir/ -f $vtop.mk $vtop"
  make \
    -j -C obj_dir/ -f $vtop.mk $vtop \
    >& $tmpdir/make_vtop.log \
    || set ERROR

  if ($?ERROR) then
    cat $tmpdir/make_vtop.log; exit 13
  endif

  if ($?VERBOSE) then
    cat $tmpdir/make_vtop.log; echo
  endif

