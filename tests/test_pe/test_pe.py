import pe
from testvectors import complete, random, test_input, test_output
from verilator import testsource, bodysource, run_verilator_test
from collections import OrderedDict
from random import randint
import pytest
import os


ops  = ['or_', 'and_', 'xor']
ops += ['lshr', 'lshl']
ops += ['add', 'sub']
# ops += ['mul0', 'mul1', 'mul2']
ops = ['abs']
# ops += ['sel']

comparison_ops = ['ge', 'le']

signed_ops = ['min', 'max', 'le', 'ge']

# def bodysource(tests, opcode, flag_sel, lut_code):
#     return f'''
#     for(int i = 0; i < {len(tests)}; i++) {{
#         unsigned int* test = tests[i];
#         top->data0 = test[0];
#         top->data1 = test[1];
#         top->bit0 = test[2];
#         top->bit1 = test[3];
#         top->bit2 = test[4];
#         top->eval();
#         printf("[lut_code=%x, opcode=%x, flag_sel=%x, Test Iteration %d] Inputs: data0=%x, data1=%x, bit0=%x, bit1=%x, bit2=%x\\n", {lut_code}, {opcode}, {flag_sel}, i, test[0], test[1], test[2], test[3], test[4]);
#         printf("    expected_res=%x, actual_res=%x\\n", test[5], top->res);
#         printf("    expected_res_p=%x, actual_res_p=%x\\n", test[6], top->res_p);
#         assert(top->res == test[5]);
#         assert(top->res_p == test[6]);
#     }}
# '''


def compile_harness(name, test, body, lut_code, cfg_d):
    harness = f"""\
#include "Vtest_pe_unq1.h"
#include "verilated.h"
#include <cassert>
#include <printf.h>

void step(Vtest_pe_unq1* top) {{
    top->clk = 0;
    top->eval();
    top->clk = 1;
    top->eval();
}}

void reset(Vtest_pe_unq1* top) {{
    top->rst_n = 1;
    top->eval();
    top->rst_n = 0;
    top->eval();
    top->rst_n = 1;
    top->eval();
}}

int main(int argc, char **argv, char **env) {{
    Verilated::commandArgs(argc, argv);
    Vtest_pe_unq1* top = new Vtest_pe_unq1;

    {test}
    reset(top);
    top->clk_en = 1;

    top->cfg_en = 1;
    top->cfg_d = {lut_code};
    top->cfg_a = 0x00;  // lut_code
    step(top);

    top->cfg_d = {cfg_d};
    top->cfg_a = 0xFF;  // opcode
    step(top);
    top->cfg_en = 0;

    {body}

    delete top;
    printf("Success!\\n");
    exit(0);
}}
"""
    with open(name, "w") as f:
        f.write(harness)

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
    if 'signed' in metafunc.fixturenames:
        metafunc.parametrize("signed", [True, False])
    if 'strategy' in metafunc.fixturenames:
        metafunc.parametrize("strategy", [complete, random])

    if 'flag_sel' in metafunc.fixturenames:
        metafunc.parametrize("flag_sel", range(0, 16))

    if 'lut_code' in metafunc.fixturenames:
        metafunc.parametrize("lut_code", range(0, 16))

@pytest.fixture
def worker_id(request):
    if hasattr(request.config, 'slaveinput'):
        return request.config.slaveinput['slaveid']
    else:
        return 'master'

def test_op(strategy, op, flag_sel, signed, worker_id):
    if flag_sel == 0xE:
        return  # Skip lut, tested separately
    bit2_mode = 0x2  # BYPASS
    bit1_mode = 0x2  # BYPASS
    bit0_mode = 0x2  # BYPASS
    data1_mode = 0x2  # BYPASS
    data0_mode = 0x2  # BYPASS
    irq_en = 0
    acc_en = 0
    if flag_sel in [0x4, 0x5, 0x6, 0x7, 0xA, 0xB, 0xC, 0xD] and not signed:  # Flag modes with N, V are signed only
        return
    lut_code = 0x00
    _op = getattr(pe, op)(flag_sel).lut(lut_code)
    cfg_d = bit2_mode << 28 | \
            bit1_mode << 26 | \
            bit0_mode << 24 | \
            data1_mode << 18 | \
            data0_mode << 16 | \
            flag_sel << 12 | \
            irq_en << 10 | \
            acc_en << 9 | \
            signed << 6 | \
            _op.opcode

    if strategy is complete:
        width = 4
        N = 1 << width
        tests = complete(_op, OrderedDict([
            ("data0", range(0, N) if not signed else range(- N // 2, N // 2)),
            ("data1", range(0, N) if not signed else range(- N // 2, N // 2)),
            ("bit0", range(0, 2)),
            ("bit1", range(0, 2)),
            ("bit2", range(0, 2)),
        ]), lambda result: (test_output("res", result[0]), test_output("res_p", result[1])))
    elif strategy is random:
        n = 16
        width = 16
        N = 1 << width
        tests = random(_op, n, OrderedDict([
            ("data0", lambda : randint(0, N) if not signed else randint(- N // 2, N // 2 - 1)),
            ("data1", lambda : randint(0, N) if not signed else randint(- N // 2, N // 2 - 1)),
            ("bit0", lambda : randint(0, 1)),
            ("bit1", lambda : randint(0, 1)),
            ("bit2", lambda : randint(0, 1))
        ]), lambda result: (test_output("res", result[0]), test_output("res_p", result[1])))

    body = bodysource(tests)
    test = testsource(tests)

    build_directory = "build_{}".format(worker_id)
    if not os.path.exists(build_directory):
        os.makedirs(build_directory)
    compile_harness(f'{build_directory}/sim_test_pe_{op}_{strategy.__name__}.cpp', test, body, lut_code, cfg_d)

    run_verilator_test('test_pe_unq1', f'sim_test_pe_{op}_{strategy.__name__}', 'test_pe_unq1', build_directory)

def test_lut(strategy, signed, lut_code, worker_id):
    op = "add"
    flag_sel = 0xE  # Lut output
    bit2_mode = 0x2  # BYPASS
    bit1_mode = 0x2  # BYPASS
    bit0_mode = 0x2  # BYPASS
    data1_mode = 0x2  # BYPASS
    data0_mode = 0x2  # BYPASS
    irq_en = 0
    acc_en = 0
    _op = getattr(pe, op)(flag_sel).lut(lut_code)
    cfg_d = bit2_mode << 28 | \
            bit1_mode << 26 | \
            bit0_mode << 24 | \
            data1_mode << 18 | \
            data0_mode << 16 | \
            flag_sel << 12 | \
            irq_en << 10 | \
            acc_en << 9 | \
            signed << 6 | \
            _op.opcode

    if strategy is complete:
        width = 4
        N = 1 << width
        tests = complete(_op, OrderedDict([
            ("data0", range(-1, 1)),  # For now we'll verify that data0/data1
            ("data1", range(-1, 1)),  # don't affect the output
            ("bit0", range(0, 2)),
            ("bit1", range(0, 2)),
            ("bit2", range(0, 2)),
        ]), lambda result: (test_output("res", result[0]), test_output("res_p", result[1])))
    elif strategy is random:
        return # We just test the LUT completely

    body = bodysource(tests)
    test = testsource(tests)

    build_directory = "build_{}".format(worker_id)
    if not os.path.exists(build_directory):
        os.makedirs(build_directory)
    compile_harness(f'{build_directory}/sim_test_pe_lut_{strategy.__name__}.cpp', test, body, lut_code, cfg_d)

    run_verilator_test('test_pe_unq1', f'sim_test_pe_lut_{strategy.__name__}', 'test_pe_unq1', build_directory)
