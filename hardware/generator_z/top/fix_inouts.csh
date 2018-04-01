#!/bin/csh -f

if ("$HOME" == "/horowitz/users/steveri") then
  echo "WARNING Setting tri-hack Because you are steveri"
  setenv VERILATOR_TRI_HACK
endif


unset TRAVIS
if ($?TRAVIS_BUILD_DIR) then
  echo "WARNING Setting tri-hack Because we are on travis"
  setenv VERILATOR_TRI_HACK
endif

if (! $?VERILATOR_TRI_HACK) then
  echo Note: not using verilator tri/inout hack
else
  echo WARNING VERILATOR TRI/INOUT HACK
  echo WARNING VERILATOR TRI/INOUT HACK
  echo WARNING VERILATOR TRI/INOUT HACK
endif

if ("$1" == "io1bit") then
  if (! $?VERILATOR_TRI_HACK) then
    echo "VHACK"
  else
    echo "NO_VHACK"
  endif
  exit
endif
  
if ("$1" == "top") then
  echo "  Part 2 (post-genesis): top.v"

  # top.v changes
  # <         pad_S0_T0,
  # >         pad_S0_T0_in, pad_S0_T0_out,
  # -----
  # <   inout pad_S0_T0;
  # >   input pad_S0_T0_in; output pad_S0_T0_out;
  # -----
  # <       .pad(pad_S0_T0),
  # >       .pad_in(pad_S0_T0_in), .pad_out(pad_S0_T0_out),

  echo "   mv genesis_verif/top.v genesis_verif/top.v.orig"
  mv genesis_verif/top.v genesis_verif/top.v.orig

  cat genesis_verif/top.v.orig \
  | sed 's/^        \(pad[^,]*\),/        \1_in, \1_out,/'\
  | sed 's/^  inout \([^;]*\);/  input \1_in; output \1_out;/'\
  | sed 's/      .pad(\(pad_S.*\)),/      .pad_in(\1_in), .pad_out(\1_out),/'\
  > genesis_verif/top.v \

  echo "   diff genesis_verif/top.v.orig genesis_verif/top.v"
  diff genesis_verif/top.v.orig genesis_verif/top.v \
    | grep S0_T0 \
    | awk '{print}    NR==2||NR==4 {print "-----"}'\
    | sed 's/^/   /'

  echo
  echo End part 2
  echo

  exit
endif


