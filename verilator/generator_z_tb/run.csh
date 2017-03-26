#!/bin/csh

#  NOTE default is NOGEN; must set -gen if want gen locally

# Travis flow (CGRAFlow/.travis.yml)
#  travis script calls "travis-test" to do the initial generate
#  travis script calls PNR to build map, io info from generated cgra_info.txt
#  builds the full parrot

# Travis flow (CGRAGenerator/.travis.yml)
#  travis script calls "travis-test" to do the initial generate
#  travis script copies pre-built io, map from example3 to $cgbuild
#  travis script calls run.csh
#  builds small parrot

# Local flow (test):
#  run.csh calls travis-test to do the initial generate
#  run.csh uses pre-built io, map files in bitstream/example3 to build config file
# builds small parrot

if ($#argv == 0) then
  # Use these defaults
  set echo
  exec $0 top_tb.cpp \
    -gen                                                  \
  # -config   ../../bitstream/example3/PNRguys_config.dat \
    -config   ../../bitstream/example3/PNRguys_mapped.xml \
    -io       ../../bitstream/example3/PNRguys_io.xml     \
    -input    io/gray_small.png                           \
    -output   /tmp/output.raw                             \
    -nclocks  1M                                          \
  || exit -1
  echo "ERROR This should never happen ("exec" should have replaced this shell)!"
  exit -1
endif  

# TODO: could create a makefile that produces a VERY SIMPLE run.csh given all these parms...(?)

# CLEANUP
foreach f (obj_dir counter.cvd tile_config.dat)
  if (-e $f) rm -rf $f
end

# Defaults
set nclocks = ''

while ($#argv)
  switch ("$1")

    case '-clean':
      exit 0;

    case '-gen':
      set GENERATE; breaksw;

    case '-config':
      set config = "$2"; shift; breaksw

    case -io:
      set iofile = "$2"; shift; breaksw

    case -input:
      set input = "$2"; shift; breaksw

    case -output:
      set output = "$2"; shift; breaksw

    case -nclocks:
      # will accept e.g. "1,000,031" or "41K" or "3M"
      set nclocks = `echo $2 | sed 's/,//g' | sed 's/K/000/' | sed 's/M/000000/'`
      set nclocks = "-nclocks $nclocks"
      shift; breaksw

    default:
      set testbench = "$1";
  endsw
  shift;
end

if (! -e "$testbench") then
  echo ""
  echo "ERROR: Testbench '$testbench' not found."
  echo ""
  echo "Maybe try one of these:"
  foreach f (*tb*.cpp)
    echo "  $0 $f"
  end
  exit -1
endif

# kiwi needs special setup for verilator
# FIXME/TODO set up kiwi so that it doesn't need this!

if (`hostname` == "kiwi") then
  echo
  echo Set verilator environment for kiwi
  setenv VERILATOR_ROOT /var/local/verilator-3.900
  set path = (/var/local/verilator-3.900/bin $path)
endif


# By default, we assume generate has already been done.
# Otherwise, user must set "-gen" to make it happen here.

echo
if (! $?GENERATE) then
  echo "No generate!"

else
  # Build CGRA 
  echo "Building CGRA because you asked for it with '-gen'..."
  pushd ../..
    ./travis-test.csh
  popd

endif

# If config files has an xml extension, use Ankita's perl script
# to turn it into a .dat/.txt configuration bitstream

echo ""
if ("$config:e" == "xml") then
  echo "Generating config bitstream 'tmpconfig.dat' from xml file '$config'..."
  perl ../../bitstream/example3/gen_bitstream.pl $config tmpconfig
  set config = tmpconfig.dat

else
  echo "Use existing config bitstream '$config'..."

endif

echo ""
echo '------------------------------------------------------------------------'
echo "BEGIN find input and output wires"
echo ""

  # If io file specified, use it to find input and output wires.
  # Otherwise, use default wire names and hope for the best.

  if ($?iofile) then
    echo "  USING WIRE NAMES FROM FILE '${iofile}':"
    grep wire_name $iofile
    echo ""

    # Why the devil didn't this work in travis!?
    #     set inwires = `set echo; sed -n /source/,/wire_name/p $iofile\
    #        | grep wire_name | sed 's/[<>]/ /g' | awk '{print $2}'`

    sed -n /source/,/wire_name/p $iofile > /tmp/tmp1
    grep wire_name /tmp/tmp1 | sed 's/[<>]/ /g' | awk '{print $2}' > /tmp/tmp2
    set inwires = `cat /tmp/tmp2`
    echo "  IN  $inwires"
   
    sed -n /sink/,/wire_name/p $iofile > /tmp/tmp1
    grep wire_name /tmp/tmp1 | sed 's/[<>]/ /g' | awk '{print $2}' > /tmp/tmp2
    set outwires = `cat /tmp/tmp2`
    echo "  OUT $outwires"
    echo ""

  else
    echo "  USING DEFAULT WIRE NAMES"

    # add4 2x2 (tile_config.dat)
    # set inwires  = (wire_0_m1_BUS16_S0_T0 wire_m1_0_BUS16_S1_T0 wire_1_m1_BUS16_S0_T2 wire_2_0_BUS16_S3_T2)
    # set outwires = (wire_0_1_BUS16_S0_T4)

    # add4 4x4 (tile_config.dat)
    # set inwires  = (wire_0_m1_BUS16_S0_T0 wire_m1_0_BUS16_S1_T0 wire_1_m1_BUS16_S0_T2 wire_4_0_BUS16_S3_T2)
    # set outwires = (wire_0_1_BUS16_S0_T4)

    # mul2/nikhil-config (PNRCONFIG.dat maybe)
    set inwires  = (wire_0_0_BUS16_S1_T0)
    set outwires = (wire_1_0_BUS16_S1_T0)

    # ../../bitstream/tmpconfigPNR.dat
    set inwires  = (wire_0_0_BUS16_S1_T0)
    set outwires = (wire_1_2_BUS16_S3_T0)
  endif

  echo "  inwires  = $inwires"
  echo "  outwires = $outwires"
  echo ""

echo "END find input and output wires"

echo ""
echo '------------------------------------------------------------------------'
echo ""

# I doubt this works anymore...
# # Substitute in a complete new custom top.v
# # (We don't really do this these days...)
# # The old switcharoo
# if ($testbench == "tbsr1.cpp") then
#   cp ./top_sr.v $gbuild/genesis_verif/top.v
# endif

set vdir = ../../hardware/generator_z/top/genesis_verif
if (! -e $vdir) then
  echo "ERROR: Could not find vfile directory"
  echo "       $vdir"
  echo "Maybe build it by doing something like:"
  echo "    (cd $vdir:h; ./run.csh; popd) |& tee tmp.log"
  exit -1
endif

echo "BEGIN top.v manipulation (won't be needed after we figure out io pads)..."
echo ""

  echo "Inserting wirenames into verilog top module '$vdir/top.v'..."
  echo
  ./run-wirehack.csh \
    -inwires "$inwires" \
    -outwires "$outwires" \
    -vtop "$vdir/top.v"

echo END top.v manipulation

echo ''
echo '------------------------------------------------------------------------'
echo ''
echo "Building the verilator simulator executable..."

  # Build the necessary switches

  # Gather the verilog files for verilator command line
  pushd $vdir >& /dev/null
    # set vfiles = (*.v *.sv)
    set vfiles = (*.v)
  popd >& /dev/null

  # So many warnings it wants to DIE!
  set myswitches = '-Wno-fatal'
  set top        = 'top'

  # Run verilator to build the simulator.

  echo
  echo verilator $myswitches -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top \
    | fold -s | sed '2,$s/^/  /' | sed 's/$/  \\/'
  echo

  verilator $myswitches -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top \
    >& /tmp/verilator.out

  set verilator_exit_status = $status

  echo 'To get the flavor of all the warnings, just showing first 40 lines of output...'
  head -n 40 /tmp/verilator.out

  if ($verilator_exit_status != 0) exit -1

echo ''
echo '------------------------------------------------------------------------'
echo ''
echo "Build the simulator..."

  # build C++ project

  echo
  echo "# Build testbench"

  echo
  echo "make \"
  echo "  VM_USER_CFLAGS='-DINWIRE=top->$inwires -DOUTWIRE=top->$outwires' \"
  echo "  -j -C obj_dir/ -f V$top.mk V$top"
  echo
  echo "TODO/FIXME this only works if there is exactly ONE each INWIRE and OUTWIRE\!\!"
  echo
  make \
    VM_USER_CFLAGS="-DINWIRE='top->$inwires' -DOUTWIRE='top->$outwires'" \
    -j -C obj_dir/ -f V$top.mk V$top || exit -1

echo ''
echo '------------------------------------------------------------------------'
echo ''
echo "Run the simulator..."
echo ''
echo '  First prepare input and output files...'

  # Prepare an input file
  #   if no input file requested => use random numbers generated internally
  #   if input file has extension ".png" => convert to raw
  #   if input file has extension ".raw" => use input file as is

  if (! $?input) then
    echo No input\; testbench will use random numbers for its check (i think)
    set in = ''

  else if ("$input:e" == "png") then
    # Convert to raw format
    echo "  Converting input file '$input' to '.raw'..."
    echo "  io/myconvert.csh $input /tmp/input.raw"
    echo
    echo -n "  "
    io/myconvert.csh $input /tmp/input.raw
    set in = "-input /tmp/input.raw"

  else if ("$input:e" == "raw") then
    echo "Using raw input from '$input'..."
    echo cp $input /tmp/input.raw
    cp $input /tmp/input.raw
    set in = "-input /tmp/input.raw"

  else
    echo "ERROR Input file '$input' has invalid extension"
    exit -1

  endif

  # echo "First few lines of input file for comparison..."
  # od -t x1 /tmp/input.raw | head

  # If no output requested, simulator will not create an output file.
  if ($?output) then
    set out = "-output $output"
  else 
    set out = ''
  endif

  echo
  echo "# Run executable simulation"

  set echo
    obj_dir/V$top \
      -config $config \
      $in \
      $out \
      $nclocks \
      || exit -1
  unset echo >& /dev/null

  echo
  echo "# Show output vs. input; output should be 2x input for most common testbench"

  if ($?input) then
    echo
    set cmd = "od -t x1 /tmp/input.raw"
    set cmd = "od -t u1 /tmp/input.raw"
    echo $cmd; $cmd | head

    echo
    set cmd = "od -t u1 $output"
    echo $cmd; $cmd | head
  endif


# Tell how to clean up (not necessary for travis VM of course)
# if (`hostname` == "kiwi") then
set pwd = `pwd`
if (! `expr $pwd : /home/travis`) then
  set gbuild = ../../hardware/generator_z/top
  cat << eof

************************************************************************
NOTE: If you want to clean up after yourself you'll want to do this:

  ./run.csh -clean
  pushd $gbuild; ./genesis_clean.cmd; popd

************************************************************************

eof
endif
