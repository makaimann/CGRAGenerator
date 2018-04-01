#!/bin/csh -f

# Can't believe I have to do this...
set path = (. $path)

# Can use this to extend time on travis
# ./my_travis_wait.csh 60 &

set VERBOSE

# Build a tmp space for intermediate files
set tmpdir = `mktemp -d /tmp/run.csh.XXX`
# set tmpdir = deleteme;     /bin/rm -rf $tmpdir/* || echo already empty
# set tmpdir = /tmp/run.csh; /bin/rm -rf $tmpdir/* || echo already empty

if (! -e $tmpdir) then
  unset ERR
  mkdir $tmpdir || set ERR
  if ($?ERR) then
    echo "Could not make dir '$tmpdir'"
    exit 99
  endif
endif


# ALWAYS BE USING MEMORY
setenv CGRA_GEN_USE_MEM 1


# setenv CGRA_GEN_ALL_REG 1

# Travis flow (CGRAFlow/.travis.yml)
#  travis script calls "generate.csh" to do the initial generate
#  travis script calls PNR to build map, io info from generated cgra_info.txt
#  builds the full parrot

# Travis flow (CGRAGenerator/.travis.yml)
#  travis script calls "generate.csh" to do the initial generate
#  travis script calls run.csh using pre-built bitstream w/embedded io info
#  builds small parrot

# Local flow (test):
#  run.csh calls generate.csh to do the initial generate
#  run.csh uses pre-built io, map files in bitstream/example3 to build config file
# builds small parrot

# DEFAULTS
set testbench = top_tb.cpp
set GENERATE  = "-gen"
set BUILD

# Sometimes may need to know what branch we are in
git branch | grep '^*' >    $tmpdir/tmp
set branch = `sed 's/^..//' $tmpdir/tmp`
rm $tmpdir/tmp


########################################################################
# Detect if running from within travis
unset TRAVIS
# Travis branch comes up as 'detached' :(
#   * (HEAD detached at a220e19)
#     master
if (`expr "$branch" : ".*detached"`) then
  echo "run.csh: I think we are running from travis"
  set TRAVIS
  set branch = `git branch | grep -v '^*' | awk '{print $1}'`
endif
echo "run.csh: I think we are in branch '$branch'"


########################################################################
# Default configuration bitstream
# INOUT/tri-state workaround for side 0 output pads
set config   = ../../bitstream/examples/pw2_16x16.bsa




set DELAY = '0,0'

# FIXED maybe
# # FIXME Yes this WILL bite my ass and very soon, I expect :(
# if ("$config" == "../../bitstream/examples/pwv2_io.bs") set DELAY = '3,3'
# 
# echo .${config}.
# echo $DELAY

# gray_small (100K cycles) still too big for 16x16
# set input     = io/gray_small.png

# pointwise w/'conv_bw' takes 4000 cycles to complete
set input     = io/conv_bw_in.png

if ("$branch" == "sixteen") set input = io/input_10x10_1to100.png


set output    = $tmpdir/output.raw
set nclocks   = "1M"
unset tracefile

if ($#argv == 1) then
  if ("$argv[1]" == '--help') then
    echo "Usage:"
    echo "    $0 <textbench.cpp> -q [-gen | -nogen] [-nobuild]"
    echo "        -usemem -allreg"
    echo "        -config <config_filename.bs>"
    echo "        -input   <input_filename.png>"
    echo "        -output <output_filename.raw>"
    echo "        -delay <ncy_delay_in>,<ncy_delay_out>"
    echo "       [-trace   <trace_filename.vcd>]"
    echo "        -nclocks <max_ncycles e.g. '100K' or '5M' or '3576602'>"
    echo "        -build  # (overrides SKIP_RUNCSH_BUILD)""
    echo
    echo "Defaults:"
    echo "    $0 top_tb.cpp \"
    echo "       $GENERATE         \"
    echo "       -config  $config \"
    echo "       -input   $input  \"
    echo "       -output  $output \"
    echo "        -delay $DELAY"
    if ($?tracefile) then
      echo "       -trace $tracefile \"
    endif
    echo "       -nclocks  $nclocks                                          \"
    echo
    exit 0
  endif
endif



# NO don't cleanup might want this later (for -nobuild)...
# # CLEANUP
# foreach f (obj_dir counter.cvd tile_config.dat)
#   if (-e $f) rm -rf $f
# end

# I GUESS 4x4 vs. 8x8 is implied by presence or absence of CGRA_GEN_USE_MEM (!!???)
# I can't find anything else that does it :(


# NEVER BE HACKMEM!
unset HACKMEM
echo "NO MORE HACKMEM 03/2018"
echo "NO MORE HACKMEM 03/2018"
echo "NO MORE HACKMEM 03/2018"
echo

while ($#argv)
  # echo "Found switch '$1'"
  switch ("$1")

    case '-hackmem':
      echo 'ERROR (run.csh) "-hackmem" no longer allowed (1803)' ; exit 13

      set HACKMEM = 1
      echo "WARNING USING TEMPORARY TERRIBLE HACKMEM"
      echo "WARNING USING TEMPORARY TERRIBLE HACKMEM"
      echo "WARNING USING TEMPORARY TERRIBLE HACKMEM"
      echo
      breaksw

    case '-no_hackmem':
      echo 'ERROR (run.csh) "-no_hackmem" no longer allowed (1803)' ; exit 13

#       unset HACKMEM
#       echo "WARNING TURNED OFF TEMPORARY TERRIBLE HACKMEM"
#       echo "WARNING TURNED OFF TEMPORARY TERRIBLE HACKMEM"
#       echo "WARNING TURNED OFF TEMPORARY TERRIBLE HACKMEM"
#       echo

      breaksw


    case '-clean':
      exit 0;

    case '-q':
      unset VERBOSE; breaksw;
    case '-v':
      set VERBOSE; breaksw;



########################################################################
    # DEPRECATED SWITCHES
    case '-4x4':
    case '-8x8':
      echo "WARNING Switch '$1' no longer valid"; breaksw

    case -usemem:
    case -newmem:
      echo "WARNING Switch '$1' no longer valid"; breaksw
      # setenv CGRA_GEN_USE_MEM 1; # always set
      breaksw;

#     case -egregious_conv21_hack:
#       set EGREGIOUS_CONV21_HACK
#       breaksw
########################################################################



    case '-gen':
      set GENERATE = '-gen'; breaksw;

    case '-nobuild':
      set GENERATE = '-nogen'; unset BUILD; breaksw;

    case '-nogen':
      set GENERATE = '-nogen'; breaksw;

    case '-build':
    case '-rebuild':
        unsetenv SKIP_RUNCSH_BUILD; breaksw



    case '-config':
      set config = "$2"; shift; breaksw

    # "bitstream" is an alias for "config"
    case '-bitstream':
      set config = "$2"; shift; breaksw

    case -io:
      echo "WARNING -io no longer supported; this switch will be ignored."
      set iofile = "$2"; shift; breaksw

    case -input:
      set input = "$2"; shift; breaksw

    case -output:
      set output = "$2"; shift; breaksw

    case -delay:
      set DELAY = "$2"; shift; breaksw

    case -trace:
      set tracefile = "$2"; shift; breaksw

    case -nclocks:
      # will accept e.g. "1,000,031" or "41K" or "3M"
      set nclocks = $2;
      shift; breaksw

    case -allreg:
      setenv CGRA_GEN_ALL_REG 1; breaksw

    # Unused / undocumented for now
    case -oldmem:
      echo "WARNING Switch '$1' no longer valid"; breaksw
      unsetenv CGRA_GEN_USE_MEM
      unsetenv CGRA_GEN_ALL_REG
      breaksw

    default:
      if (`expr "$1" : "-"`) then
        echo "ERROR: Unknown switch '$1'"
        exec $0 --help
        exit -1
      endif
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


# if ($?VERBOSE) then
if (1) then
  # Backslashes line up better when printed...
  echo "Running with the following switches:"
  echo "$0 top_tb.cpp \"
  if (! $?BUILD) echo "   -nobuild                    \"
  echo "   $GENERATE                    \"
  echo "   -config   $config   \"
  #echo "   -io       $iofile   \"
  echo "   -input    $input  \"
  echo "   -output   $output    \"
  echo "   -delay   $DELAY    \"
  if ($?tracefile) then
    echo "   -trace $tracefile \"
  endif
  echo "   -nclocks  $nclocks                 \"
endif

if (! -e $config) then
  echo "run.csh: ERROR Cannot find config file '$config'"
  exit 13
endif





# if (`expr "$config" : ".*lbuf.*"`) then
#   if (! $?HACKMEM) then
#     echo
#     echo "run.csh: ERROR '$config' looks like an lbuf config file"
#     echo "run.csh: ERROR should be using hackmem flag, yes?"
#     exit 13
#   endif
# endif


if (`expr "$config" : ".*lbuf.*"`) then
  if ($?HACKMEM) then
    echo
    echo "run.csh: ERROR '$config' looks like an lbuf config file"
    echo "run.csh: ERROR should NO LONGER be using hackmem flag, yes?"
    exit 13
  endif
endif





unset io_hack
grep -i ffffffff $config > /tmp/tmp && set io_hack
if ($?io_hack) then
  echo 'ERROR Config file $config appears to be trying to use the old I/O hack:'
  cat /tmp/tmp; /bin/rm /tmp/tmp
  echo 'ERROR We no longer support I/O hacks, please use I/O pads instead'
  echo
  exit 13
endif



# Turn nclocks into an integer.
set nclocks = `echo $nclocks | sed 's/,//g' | sed 's/K/000/' | sed 's/M/000000/'`
set nclocks = "-nclocks $nclocks"

# which verilator

if   ($?VERBOSE) set VSWITCH = '-v'
if (! $?VERBOSE) set VSWITCH = '-q'

set vtop = 'Vtop'
if (! $?BUILD) then
  echo ""
  echo "Skipping generate and build b/c you asked me to..."
  goto RUN_SIM
endif


##############################################################################
# By default, we assume generate has already been done.
# Otherwise, user must set "-gen" to make it happen here.

echo
# if (! $?GENERATE) then
if ("$GENERATE" == "-nogen") then
  echo "run.csh: No generate!"
  echo "run.csh: Not building CGRA because you asked for it with '-nogen'..."
else
  # echo "run.csh: Building CGRA because you asked for it with '-gen'..."
  echo "run.csh: Building CGRA because it's the default..."
  if ($?VERBOSE) echo "run.csh: ../../bin/generate.csh $VSWITCH"
  ../../bin/generate.csh $VSWITCH || exit -1
endif

##############################################################################
# Remove LUT commands from bitstream (I guess we don't do this no more)
# Which is good because it's probably *so busted*
unset LUT_HACK
if ($?LUT_HACK) then
  echo "run.csh: ./run-luthack.csh $config"
  ./run-luthack.csh $config
endif

########################################################################
# Now process bitstream file $config for IO information

set ctail = $config:t
set croot = $ctail:r
set config_io = $tmpdir/${croot}io

# Are you kidding me
set path = ($path .)

# Clean up config file for verilator use
grep -v '#' $config | grep . > $tmpdir/tmpconfig
set config = $tmpdir/tmpconfig

if ($?VERBOSE) then
  echo
  head $config
  echo ...
  tail $config
endif

# Quick check of goodness in config file
unset bad_config
set c = '[0-9a-fA-F]'
set goodline = "$c$c$c$c$c$c$c$c $c$c$c$c$c$c$c$c"
egrep -v "$goodline" $config > /tmp/tmp$$ && set bad_config
if ($?bad_config) then
  echo
  echo "ERROR Config file '$config' looks bad, man. Bad line(s) include:"
  cat /tmp/tmp$$ | sed 's/^/> /'
  exit 13
endif

set vdir = ../../hardware/generator_z/top/genesis_verif
if (! -e $vdir) then
  echo "ERROR: Could not find vfile directory"
  echo "       $vdir"
  echo "Maybe build it by doing something like:"
  echo "    (cd $vdir:h; ./run.csh; popd) |& tee tmp.log"
  exit -1
endif

echo ''
echo '------------------------------------------------------------------------'
echo "Building the verilator simulator executable..."

if ($?SKIP_RUNCSH_BUILD) then
  echo "OOPS MAYBE NOT; FOUND ENV VAR 'SKIP_RUNCSH_BUILD'"
  echo "OOPS MAYBE NOT; FOUND ENV VAR 'SKIP_RUNCSH_BUILD'"
  echo "OOPS MAYBE NOT; FOUND ENV VAR 'SKIP_RUNCSH_BUILD'"
endif


  # (Temporary (I hope)) SRAM hack(s)

  echo
  echo '  SRAM hack'
  echo '  SRAM hack'
  echo '  SRAM hack'
  if ($?CGRA_GEN_USE_MEM) then
     cp ./sram_stub.v $vdir/sram_512w_16b.v
     ls -l $vdir/sram*
  endif

#   # Temporary wen/ren hacks.  
#   if ($?HACKMEM) then
#     # In memory_core_unq1.v, change:
#     #   assign wen_in_int = (`$ENABLE_CHAIN`)?chain_wen_in:xwen;
#     # To:
#     #   assign wen_in_int = WENHACK
# 
#     unset ERR
#     egrep '^assign wen_in_int = .*' $vdir/memory_core_unq1.v || set ERR
#     if ($?ERR) then
#       echo
#       echo "run.csh: ERROR looks like WENHACK would FAIL"
#       exit 13
#     endif
# 
#     # ls -l $vdir
#     mv $vdir/memory_core_unq1.v $tmpdir/memory_core_unq1.v.orig
#     cat $tmpdir/memory_core_unq1.v.orig \
#       | sed 's/^assign wen_in_int = .*/assign wen_in_int = WENHACK;/' \
#       > $vdir/memory_core_unq1.v
# 
#     # old
#     #  | sed 's/^assign wen = .*/assign wen = WENHACK;/' \
# 
# 
# 
#     # No longer doing:
#     #  | sed 's/assign int_ren = .*/assign int_ren = 1;/' \
#     #  | sed 's/assign int_wen = .*/assign int_wen = 1;/' \
#     #  | sed 's/assign wen = .*/assign wen = 1;/' \
# 
#     echo
#     echo '------------------------------------------------------------------------'
#     echo WARNING REWROTE memory_core_unq1.v BECAUSE TEMPORARY TERRIBLE MEMHACK
#     echo WARNING REWROTE memory_core_unq1.v BECAUSE TEMPORARY TERRIBLE MEMHACK
#     echo WARNING REWROTE memory_core_unq1.v BECAUSE TEMPORARY TERRIBLE MEMHACK
#     echo diff $tmpdir/memory_core_unq1.v.orig $vdir/memory_core_unq1.v
#     diff $tmpdir/memory_core_unq1.v.orig $vdir/memory_core_unq1.v
#     echo '------------------------------------------------------------------------'
#     echo
#     echo
# 
#   endif

echo 'Note: No more IO hacks;'
echo 'pixels must arrive via pad_S2_T[8:15] aka wire_2_1_BUS16_S0_T0'
echo 'and           exit via pad_S0_T[7:0] aka wire_2_17_BUS16_S0_T0'



echo ''
echo '------------------------------------------------------------------------'
echo "run.csh: Build the simulator..."

if ($?SKIP_RUNCSH_BUILD) then
  echo "WARNING SKIPPING SIMULATOR BUILD B/C FOUND ENV VAR 'SKIP_RUNCSH_BUILD'"
  echo "WARNING SKIPPING SIMULATOR BUILD B/C FOUND ENV VAR 'SKIP_RUNCSH_BUILD'"
  echo "WARNING SKIPPING SIMULATOR BUILD B/C FOUND ENV VAR 'SKIP_RUNCSH_BUILD'"
  goto RUN_SIM
endif

# How about skip verilator build if:
# 0. Running on travis AND
# 1. obj_dir/Vtop exists
# 2. hackmem is in place ==> NO MORE HACKMEM

if (! $?TRAVIS_BUILD_DIR) goto BUILD_SIM
# ELSE
  if (-e obj_dir/Vtop) then
    echo Found existing obj_dir/Vtop

  # NO MORE WENHACK!!!
  #   set vdir = ../../hardware/generator_z/top/genesis_verif
  #   if (-e $vdir/memory_core_unq1.v) then 
  #     echo Found $vdir/memory_core_unq1.v
  #     unset foundhack
  #     egrep 'assign.*WENHACK' $vdir/memory_core_unq1.v && set foundhack
  #     if ($?foundhack) then
  #       echo Found memhack
  #       echo Found Vtop and memhack = skipping verilator build
  #       goto RUN_SIM
  #     else
  #       echo No memhack, must rebuild
  #     endif

    echo Found Vtop = skipping verilator build
    goto RUN_SIM

    endif
  endif



BUILD_SIM:
if ($?tracefile) then
  echo build_simulator.csh $VSWITCH $testbench $tracefile
  ./build_simulator.csh $VSWITCH $testbench $tracefile || exit 13
else
  echo build_simulator.csh $VSWITCH $testbench
  ./build_simulator.csh $VSWITCH $testbench || exit 13
endif


RUN_SIM:
echo '------------------------------------------------------------------------'
echo "run.csh: Run the simulator..."
echo ''

# Check WENHACK status
    # In memory_core_unq1.v, look for:
    #   assign wen_in_int = WENHACK
    set vdir = ../../hardware/generator_z/top/genesis_verif
    egrep '^assign.*WENHACK' $vdir/memory_core_unq1.v && set WENHACKED
    if ($?WENHACKED) then
      echo 'WARNING Looks like WENHACK is ON'
      echo 'WARNING Looks like WENHACK is ON'
      echo 'WARNING Looks like WENHACK is ON'
      echo 'ERROR WENHACK SHOULD NOT EXIST ANY MORE'; exit 13
    else
      echo 'WARNING Looks like WENHACK is OFF'
      echo 'WARNING Looks like WENHACK is OFF'
      echo 'WARNING Looks like WENHACK is OFF'
    endif


if ($?VERBOSE) echo '  First prepare input and output files...'

  # Prepare an input file
  #   if no input file requested => use random numbers generated internally
  #   if input file has extension ".png" => convert to raw
  #   if input file has extension ".raw" => use input file as is

  set iroot = $input:t; set iroot = $iroot:r

#   if (! $?input) then
#     # SR 3/2018 Yeah Im pretty sure this dont work no more...
#     # echo No input\; testbench will use random numbers for its check (i think)
#     # set in = ''
#     echo 'ERROR (run.csh) no input file found'; exit 13
# 
#   else

  if ("$input:e" == "png") then
    if ($?VERBOSE) then
      echo "  Converting input file '$input' to '$tmpdir/$iroot.raw'..."
      echo "  io/myconvert.csh $input $tmpdir/$iroot.raw"
      echo
      echo -n "  "
      io/myconvert.csh $input $tmpdir/$iroot.raw || exit 13
    else
      io/myconvert.csh -q $input $tmpdir/$iroot.raw || exit 13
    endif
    set input = "$tmpdir/$iroot.raw"

  else if ("$input:e" == "raw") then
    if ($?VERBOSE) then
      echo "  Using raw input from '$input'..."
      # echo "  cp $input $tmpdir/$iroot.raw"
    endif
    # cp $input $tmpdir/$iroot.raw

  else
    echo "ERROR run.csh: Input file '$input' has invalid extension"
    exit -1

  endif
  # set in = "-input $tmpdir/$iroot.raw"
  # set input = "$tmpdir/$iroot.raw"



  # echo "First few lines of input file for comparison..."
  # od -t x1 $tmpdir/input.raw | head

  # If no output requested, simulator will not create an output file.
  set out = ''
  if ($?output) then
      set out = "-output $output"
  endif

  set delay = "-delay $DELAY"

  # If no trace requested, simulator will not create a waveform file.
  set trace = ''
  if ($?tracefile) then
    set trace = "-trace $tracefile"
  endif

  echo
  echo "run.csh: Run executable simulation"

  # 00020: Two times 19 = 38  *PASS*
  # 00021: Two times 22 = 44  *PASS*
  # 00022: Two times 23 = 46  *PASS*
  # ...
  # 00058: Two times 31 = 62  *PASS*
  # 00059: Two times 29 = 58  *PASS*

  # For 'quiet' execution, use these two filters to limit output;
  # Otherwise just cat everything to stdout
  if (! $?VERBOSE) then
    set quietfilter = (grep -v "scanned config")
    set qf2 = (grep -v "^000[23456789].*Two times")
  else
    set quietfilter = (cat)
    set qf2         = (cat)
  endif

  # This is ugly.  -nobuild skips config-file processing so redo here.
  if (! $?BUILD) then
    # Clean up config file for verilator use
    grep -v '#' $config | grep . > $tmpdir/tmpconfig
    set config = $tmpdir/tmpconfig
  endif

  # Quick check of goodness in config file (again)
  unset bad_config
  set c = '[0-9a-fA-F]'
  set goodline = "$c$c$c$c$c$c$c$c $c$c$c$c$c$c$c$c"
  egrep -v "$goodline" $config > /tmp/tmp$$ && set bad_config
  if ($?bad_config) then
    echo
    echo "ERROR Config file '$config' looks bad, man. Bad line(s) include:"
    cat /tmp/tmp$$ | sed 's/^/> /'
    exit 13
  endif

  if ($?VERBOSE) then
    echo
    echo "BITSTREAM '$config':"
    cat $config
  endif

  echo
  echo "run.csh: TIME NOW: `date`"
  echo "run.csh: $vtop -output $output:t"

  # OOPS big parrot won't work in travis if output gets filtered...
  # Must have the printf every 10K cycles
  set quietfilter = (cat)
  set qf2         = (cat)


  # FIXME note the '|| exit -1" below is USELESS
  if ($?VERBOSE) set echo
    obj_dir/$vtop \
      -config $config \
      -input $input \
      $out \
      $delay \
      $trace \
      $nclocks \
      | tee $tmpdir/run.log.$$ \
      | $quietfilter:q | $qf2:q \
      || exit -1
  unset echo >& /dev/null
  echo -n " TIME NOW: "; date

  unset FAIL
  grep FAIL   $tmpdir/run.log.$$ && set FAIL
  grep %Error $tmpdir/run.log.$$ && set FAIL


  echo
  echo "# Show output vs. input; output should be 2x input for most common testbench"

  if ($?input) then
    echo
    ls -l $tmpdir/$iroot.raw $output

    if ("$output:t" == "conv_1_2_CGRA_out.raw") then
      # echo; set cmd = "od -t u1 $output"; echo $cmd; $cmd | head

      echo; echo "FOUND conv_1_2 output; converting to 9x9..."
      ./bin/conv_1_2_convert < $output > $tmpdir/tmp.raw
      mv $tmpdir/tmp.raw $output
      ls -l $output

      # echo; set cmd = "od -t u1 $output"; echo $cmd; $cmd | head

    endif

    if ("$output:t" == "conv_bw_CGRA_out.raw") then
      echo; echo "FOUND conv_bw output; converting to 62x62..."
      ./bin/crop31 < $output > $tmpdir/tmp.raw
      mv $tmpdir/tmp.raw $output
      ls -l $output
    endif

    echo
    set cmd = "od -t x1 $tmpdir/$iroot.raw"
    set cmd = "od -t u1 $tmpdir/$iroot.raw"
  # echo $cmd; $cmd | head
    echo $cmd; $cmd | head; echo ...; $cmd | tail -n 3

    echo
    set cmd = "od -t u1 $output"
  # echo $cmd; $cmd | head
    echo $cmd; $cmd | head; echo ...; $cmd | tail -n 3
  endif


  if ($?FAIL) exit -1

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
