import pytest
import subprocess
import pe
from testvectors import complete, random
from verilator import compile, run_verilator_test
import ncsim
import delegator
import os

def run_ncsim_test(op, opcode, tests, strategy):
    return
    if os.environ.get("TRAVIS", True):
        # Skip on Travis because cadence tools not available
        # FIXME: Should check for cadence tools available instead
        return
    ncsim.compile(f'test_{op}_{strategy.__name__}', opcode, tests)
    RTL_FOLDER = "../../hardware/generator_z/top/genesis_verif"
    result = delegator.run(f"""
irun -top test_pe_comp_unq1_tb -timescale 1ns/1ps -l irun.log -access +rwc -notimingchecks -input ../../hardware/generator_z/impl/verif/cmd.tcl build/ncsim_test_{op}_{strategy.__name__}_tb.v /nobackup/nikhil3/arm_mems/arm/tsmc/cln40g/sram_sp_hsc_rvt_hvt_rvt/r10p2/sram_512w_16b/sram_512w_16b.v {RTL_FOLDER}/cb_unq1.v {RTL_FOLDER}/cb_unq2.v {RTL_FOLDER}/cb_unq3.v {RTL_FOLDER}/global_signal_tile_unq1.v {RTL_FOLDER}/io1bit_unq1.v {RTL_FOLDER}/io1bit_unq2.v {RTL_FOLDER}/io1bit_unq3.v {RTL_FOLDER}/io1bit_unq4.v {RTL_FOLDER}/jtag_unq1.sv {RTL_FOLDER}/memory_core_unq1.v {RTL_FOLDER}/memory_tile_unq1.v {RTL_FOLDER}/mem_unq1.v {RTL_FOLDER}/pe_tile_new_unq1.v {RTL_FOLDER}/sb_unq1.v {RTL_FOLDER}/sb_unq2.v {RTL_FOLDER}/sb_unq3.v  {RTL_FOLDER}/test_cmpr.sv {RTL_FOLDER}/test_full_add.sv {RTL_FOLDER}/test_lut.sv {RTL_FOLDER}/test_mult_add.sv {RTL_FOLDER}/test_opt_reg.sv {RTL_FOLDER}/test_pe_comp_unq1.sv {RTL_FOLDER}/test_pe_unq1.sv {RTL_FOLDER}/test_shifter_unq1.sv {RTL_FOLDER}/top.v
    """)
    assert not result.return_code, result.out + "\n" + result.err
    assert "Failed!" not in result.out, result.out + "\n" + result.err

ops  = ['or_', 'and_', 'xor']
# ops += ['inv']
ops += ['lshr', 'lshl']
# ops += ['ashr']
ops += ['add', 'sub']
ops += ['mul0', 'mul1', 'mul2']
ops += ['abs']
ops += ['sel']

comparison_ops = ['ge', 'le']

signed_ops = ['min', 'max', 'le', 'ge']
def pytest_generate_tests(metafunc):
    if 'op' in metafunc.fixturenames:
        metafunc.parametrize("op", ops)
    if 'signed_op' in metafunc.fixturenames:
        metafunc.parametrize("signed_op", signed_ops)
        metafunc.parametrize("signed", [True, False])
    if 'const_value' in metafunc.fixturenames:
        metafunc.parametrize("const_value", range(16))
    if 'comparison_op' in metafunc.fixturenames:
        metafunc.parametrize("comparison_op", comparison_ops)
        metafunc.parametrize("signed", [True, False])
    if 'strategy' in metafunc.fixturenames:
        metafunc.parametrize("strategy", [complete, random])


def test_op(op, strategy):
    a = getattr(pe, op)()

    if strategy is complete:
        n = 16
    else:
        n = 256
    tests = strategy(a._alu, n, 16)

    compile(f'test_{op}_{strategy.__name__}', 'test_pe_comp_unq1', a.opcode , tests)
    run_verilator_test('test_pe_comp_unq1', f'sim_test_{op}_{strategy.__name__}', 'test_pe_comp_unq1')
    run_ncsim_test(op, a.opcode, tests, strategy)

def test_signed_op(signed_op, signed, strategy):
    a = getattr(pe, signed_op)(signed)

    if strategy is complete:
        n = 16
    else:
        n = 256
    tests = strategy(a._alu, n, 16)

    compile(f'test_{signed_op}_{strategy.__name__}', 'test_pe_comp_unq1', a.opcode | signed << 6, tests)
    run_verilator_test('test_pe_comp_unq1', f'sim_test_{signed_op}_{strategy.__name__}', 'test_pe_comp_unq1')
    run_ncsim_test(signed_op, a.opcode | signed << 6, tests, strategy)

def test_comparison_op(comparison_op, signed, strategy):
    a = getattr(pe, comparison_op)(signed)

    if strategy is complete:
        n = 16
    else:
        n = 16
    tests = strategy(a._alu, n, 16)

    compile(f'test_{comparison_op}_{strategy.__name__}', 'test_pe_comp_unq1', a.opcode | signed << 6, tests)
    run_verilator_test('test_pe_comp_unq1', f'sim_test_{comparison_op}_{strategy.__name__}', 'test_pe_comp_unq1')
    run_ncsim_test(comparison_op, a.opcode | signed << 6, tests, strategy)

# @pytest.mark.skip
# def test_const(const_value, strategy):
#     a = pe.const(const_value)
# 
#     tests = strategy(a, 4, 16)
# 
#     compile(f'test_const_{strategy.__name__}', 'test_pe_comp_unq1', a.opcode, tests)
#     run_verilator_test('test_pe_comp_unq1', f'sim_test_const_{strategy.__name__}', 'test_pe_comp_unq1')
