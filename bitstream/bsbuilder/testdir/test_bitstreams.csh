#!/bin/csh -f

if ("$1" == "--help") then
  echo 'test_bitstreams.csh tmpdir'
  echo 'test_bitstreams.csh tmpdir pointwise'
  echo 'test_bitstreams.csh tmpdir pointwise conv_1_2 conv_2_1 conv_3_1 conv_bw'
  exit
endif

set buildswitch = ''
if ("$1" == "-nobuild") then
  set buildswitch = '-nobuild'
  shift
endif


if (! -d $1) then
  echo 'Where are the test.bsa input files?'
  echo "Example: $0:t /tmp/build42/"
  exit -1
endif
set tmpdir = $1

# Oops maybe tmpdir must be a full path
set tmpdir = `(cd $tmpdir; pwd)`

# Any remaining arguments constitute the list of benchmarks to run
shift
if ($#argv) then
  set bmarks = ($*)
else 
  # Do them in order
  set bmarks = (pointwise conv_2_1 conv_3_1 conv_bw)
  set bmarks = (pointwise conv_1_2 conv_2_1 conv_3_1 conv_bw)
endif

set scriptpath = `readlink -f $0`
set scriptpath = $scriptpath:h
cd $scriptpath

# Script is maybe in $gen/bitstream/bsbuilder/testdir
set gen = `(cd ../../..; pwd)`
set v =  $gen/verilator/generator_z_tb


# DB for delay, extracted below
#   - make build/pointwise.correct.txt DELAY=0,0   
#   - make build/conv_1_2.correct.txt  DELAY=1,0   
#   - make build/conv_2_1.correct.txt  DELAY=10,0  
#   - make build/conv_3_1.correct.txt  DELAY=20,0  
#   - make build/conv_bw.correct.txt   DELAY=130,0 

if (-e $tmpdir/test_results.log) rm $tmpdir/test_results.log

unset TRACE
foreach b ($bmarks)
  echo "------------------------------------------------------------------------"
  echo "TESTING $b"

  set bsa   = $tmpdir/$b.bsa
  set input = $scriptpath/examples/${b}_input.raw
  set delay = `grep ${b}.correct $0:t | sed 's/.*DELAY=\(.*\)/\1/'`

  # Note this output name is 'magic' and directs run.csh to do things :(
  # Maybe (FIXME)
  set out = $tmpdir/${b}_CGRA_out.raw

  set tswitch = ''
  if ($?TRACE) set tswitch = "-trace $b.vcd"


   # NO MORE HACKMEM!
   # ./run.csh $tswitch -hackmem -config $bsa -input $input -output $out -delay $delay \


  setenv SERPENT_HACK
  (\
   cd $v; \
   ./run.csh $buildswitch $tswitch -config $bsa -input $input -output $out -delay $delay \
  ) || exit 13


  echo "FINAL COMPARE FOR SUMMARY"
  ./compare_images.csh $b $out examples/${b}_halide_out.raw\
  | tee -a $tmpdir/test_results.log

end

grep RESULT $tmpdir/test_results.log

# Clean up
# No! Not my job!
# /bin/rm -rf $tmpdir
