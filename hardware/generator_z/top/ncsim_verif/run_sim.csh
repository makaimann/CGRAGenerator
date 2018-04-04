#!/bin/tcsh
set RTL_FOLDER="../genesis_verif"
rm -rf INCA_libs irun.*
irun -top test_top -timescale 1ns/1ps -l irun.log -access +rwc -notimingchecks \
-input \
$RTL_FOLDER/../ncsim_verif/cmd.tcl \
$RTL_FOLDER/cb_unq1.v  \
$RTL_FOLDER/cb_unq2.v \
$RTL_FOLDER/cfg_and_dbg_unq1.sv \
$RTL_FOLDER/cfg_ifc_unq1.sv \
$RTL_FOLDER/clocker_unq1.sv \
$RTL_FOLDER/fifo_control_unq1.v \
$RTL_FOLDER/flop_unq1.sv \
$RTL_FOLDER/flop_unq2.sv \
$RTL_FOLDER/flop_unq3.sv \
$RTL_FOLDER/global_controller_unq1.sv \
$RTL_FOLDER/global_signal_tile_unq1.v \
$RTL_FOLDER/input_sr_unq1.v \
$RTL_FOLDER/io16bit_unq1.v \
$RTL_FOLDER/io16bit_unq2.v \
$RTL_FOLDER/io16bit_unq3.v \
$RTL_FOLDER/io16bit_unq4.v \
$RTL_FOLDER/io1bit_unq1.v \
$RTL_FOLDER/io1bit_unq2.v \
$RTL_FOLDER/io1bit_unq3.v \
$RTL_FOLDER/io1bit_unq4.v \
$RTL_FOLDER/JTAGDriver.sv \
$RTL_FOLDER/jtag_unq1.sv \
$RTL_FOLDER/linebuffer_control_unq1.v \
$RTL_FOLDER/memory_core_unq1.v \
$RTL_FOLDER/memory_tile_unq1.v \
$RTL_FOLDER/mem_unq1.v \
$RTL_FOLDER/output_sr_unq1.v \
$RTL_FOLDER/pe_tile_new_unq1.sv \
$RTL_FOLDER/sb_unq1.v \
$RTL_FOLDER/sb_unq2.v \
$RTL_FOLDER/sb_unq3.v \
$RTL_FOLDER/tap_unq1.sv \
$RTL_FOLDER/template_ifc_unq1.sv \
$RTL_FOLDER/test_cmpr.sv \
$RTL_FOLDER/test_debug_reg.sv \
$RTL_FOLDER/test_full_add.sv \
$RTL_FOLDER/test_lut.sv \
$RTL_FOLDER/test_mult_add.sv \
$RTL_FOLDER/test_opt_reg_file.sv \
$RTL_FOLDER/test_opt_reg.sv \
$RTL_FOLDER/test_pe_comp_unq1.sv \
$RTL_FOLDER/test_pe_unq1.sv \
$RTL_FOLDER/test_shifter_unq1.sv \
$RTL_FOLDER/test_top.sv \
$RTL_FOLDER/test_unq1.sv \
$RTL_FOLDER/top.v \
$SYNOPSYS/dw/sim_ver/DW_tap.v \
$RTL_FOLDER/../sram_512w_16b.v 
