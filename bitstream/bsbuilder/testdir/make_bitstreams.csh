#!/bin/csh -f

if ($#argv == 0) then
  echo 'Where should I put the bsa output files?'
  echo "Example: $0:t /tmp/build42/"
  exit 13
endif

if ("$1" == "--help") then
  echo 'make_bitstreams.csh tmpdir'
  echo 'make_bitstreams.csh tmpdir pointwise'
  echo 'make_bitstreams.csh tmpdir pointwise conv_1_2 conv_2_1 conv_3_1 conv_bw'
  exit
endif

if (! -d $1) then
  echo 'Where should I put the bsa output files?'
  echo "Example: $0:t /tmp/build42/"
  exit 13
endif
set tmp = $1

# Any remaining arguments constitute the list of benchmarks to run
shift
if ($#argv) then
  set bmarks = ($*)
else 
  # Do benchmarks in order
  set bmarks = (conv_1_2)
  set bmarks = (pointwise conv_2_1 conv_3_1 conv_bw)
  set bmarks = (pointwise conv_1_2 conv_2_1 conv_3_1 conv_bw)
endif

set scriptpath = `readlink -f $0`
set scriptpath = $scriptpath:h
cd $scriptpath

# Script is maybe in $gen/bitstream/bsbuilder/testdir
set gen = `(cd ../../..; pwd)`
alias json2dot $gen/testdir/graphcompare/json2dot.py


echo "set tmp = $tmp"
echo 'set gen = CGRAGenerator'
echo 'cd $gen/bitstream/bsbuilder'
echo 'alias json2dot $gen/testdir/graphcompare/json2dot.py'
echo ''

set t = '$tmp'
foreach b ($bmarks)
  set result = 'PASSED'
  echo "------------------------------------------------------------------------"
  echo "PROCESSING $b"

  set map_json = examples/${b}_mapped.json
  set map_dot  =   ${b}_mapped.dot
  set bsb      =   ${b}.bsb
  set bsa      =   ${b}.bsa

  echo "  json2dot < $map_json > $t/$map_dot"
  json2dot < $map_json > $tmp/$map_dot || exit 13

  echo "cmp $tmp/$map_dot examples/$map_dot"
  cmp $tmp/$map_dot examples/$map_dot || set result = 'FAILED'
  echo ""


  echo "  ../serpent.py $t/$map_dot -o $t/$bsb > $t/$b.log.serpent"
  ../serpent.py $tmp/$map_dot -o $tmp/$bsb > $tmp/$b.log.serpent || exit 13

  echo "  cmp $tmp/$bsb examples/$bsb"
  cmp $tmp/$bsb examples/$bsb || set result = 'FAILED'
  echo ""

  if ($?VERBOSE) then
    echo ''
    echo '========================================================================'
    echo "BSB FILE $bsb"
    echo '========================================================================'
    cat $bsb
    echo ''
    echo ''
    echo ''
  endif

  echo "  ../bsbuilder.py < $tmp/$bsb > $tmp/$bsa"
  # ../bsbuilder.py -v < $tmp/$bsb | sed -n '/FINAL PASS/,$p' | sed '1,2d' > $tmp/$bsa || exit 13
  ../bsbuilder.py < $tmp/$bsb > $tmp/$bsa || exit 13

  echo "  cmp $tmp/$bsa examples/$bsa"
  ls -l examples/$bsa $tmp/$bsa
  cmp $tmp/$bsa examples/$bsa || set result = 'FAILED'


  if ($?VERBOSE) then
    echo ''
    echo '========================================================================'
    echo "BSA FILE $bsa"
    echo '========================================================================'
    cat $bsa
    echo ''
  endif

  echo "TEST $b $result"
  echo ""

  # if ($result == "FAILED") exit 13
  if ($result == "FAILED") then
    echo "WARNING comparison failed; will attempt to recover"
  endif

end

# Clean up
# No! Not my job!
# /bin/rm -rf $tmp
