from pe import abs, and_
from testvectors import complete
from verilator import compile, run_verilator_test
import ncsim
import delegator
import os

def test_abs():
    a = abs()

    tests = complete(a, 4, 16)

    compile('test_abs_complete', 'test_pe_comp_unq1', a.opcode, tests)
    run_verilator_test('test_pe_comp_unq1', 'sim_test_abs_complete', 'test_pe_comp_unq1')
    if os.environ.get("TRAVIS", True):
        # Skip on Travis because cadence tools not available
        # FIXME: Should check for cadence tools available instead
        return
    ncsim.compile('test_abs_complete', a.opcode, tests)
    RTL_FOLDER = "../../hardware/generator_z/top/genesis_verif"
    # irun -top tb -timescale 1ns/1ps -l irun.log -access +rwc -notimingchecks -input cmd.tcl build/ncsim_test_abs_complete_tb.v /nobackup/nikhil3/arm_mems/arm/tsmc/cln40g/sram_sp_hsc_rvt_hvt_rvt/r10p2/sram_512w_16b/sram_512w_16b.v {RTL_FOLDER}/cb_unq1.v {RTL_FOLDER}/cb_unq2.v {RTL_FOLDER}/cb_unq3.v {RTL_FOLDER}/global_controller_unq1.v {RTL_FOLDER}/global_signal_tile_unq1.v {RTL_FOLDER}/io1bit_unq1.v {RTL_FOLDER}/io1bit_unq2.v {RTL_FOLDER}/io1bit_unq3.v {RTL_FOLDER}/io1bit_unq4.v {RTL_FOLDER}/jtag_unq1.sv {RTL_FOLDER}/memory_core_unq1.v {RTL_FOLDER}/memory_tile_unq1.v {RTL_FOLDER}/mem_unq1.v {RTL_FOLDER}/pe_tile_new_unq1.v {RTL_FOLDER}/pe_tile_new_unq2.v {RTL_FOLDER}/sb_unq1.v {RTL_FOLDER}/sb_unq2.v {RTL_FOLDER}/sb_unq3.v  {RTL_FOLDER}/test_cmpr.sv {RTL_FOLDER}/test_full_add.sv {RTL_FOLDER}/test_lut.sv {RTL_FOLDER}/test_mult_add.sv {RTL_FOLDER}/test_opt_reg.sv {RTL_FOLDER}/test_pe_comp_unq1.sv {RTL_FOLDER}/test_pe_unq1.sv {RTL_FOLDER}/test_shifter_unq1.sv {RTL_FOLDER}/top.v
    result = delegator.run(f"""
irun -top test_pe_comp_unq1_tb -timescale 1ns/1ps -l irun.log -access +rwc -notimingchecks -input ../../hardware/generator_z/impl/verif/cmd.tcl build/ncsim_test_abs_complete_tb.v /nobackup/nikhil3/arm_mems/arm/tsmc/cln40g/sram_sp_hsc_rvt_hvt_rvt/r10p2/sram_512w_16b/sram_512w_16b.v {RTL_FOLDER}/cb_unq1.v {RTL_FOLDER}/cb_unq2.v {RTL_FOLDER}/cb_unq3.v {RTL_FOLDER}/global_signal_tile_unq1.v {RTL_FOLDER}/io1bit_unq1.v {RTL_FOLDER}/io1bit_unq2.v {RTL_FOLDER}/io1bit_unq3.v {RTL_FOLDER}/io1bit_unq4.v {RTL_FOLDER}/jtag_unq1.sv {RTL_FOLDER}/memory_core_unq1.v {RTL_FOLDER}/memory_tile_unq1.v {RTL_FOLDER}/mem_unq1.v {RTL_FOLDER}/pe_tile_new_unq1.v {RTL_FOLDER}/sb_unq1.v {RTL_FOLDER}/sb_unq2.v {RTL_FOLDER}/sb_unq3.v  {RTL_FOLDER}/test_cmpr.sv {RTL_FOLDER}/test_full_add.sv {RTL_FOLDER}/test_lut.sv {RTL_FOLDER}/test_mult_add.sv {RTL_FOLDER}/test_opt_reg.sv {RTL_FOLDER}/test_pe_comp_unq1.sv {RTL_FOLDER}/test_pe_unq1.sv {RTL_FOLDER}/test_shifter_unq1.sv {RTL_FOLDER}/top.v
    """)
    assert not result.return_code, result.out + "\n" + result.err
    assert "Failed!" not in result.out, result.out + "\n" + result.err

def test_and():
    a = and_()

    tests = complete(a, 4, 16)
    compile('test_and_complete', 'test_pe_comp_unq1', a.opcode, tests)
    run_verilator_test('test_pe_comp_unq1', 'sim_test_and_complete', 'test_pe_comp_unq1')
