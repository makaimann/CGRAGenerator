import pe
from testvectors import complete, random
from verilator import testsource, run_verilator_test


ops  = ['or_', 'and_', 'xor']
ops += ['lshr', 'lshl']
ops += ['add', 'sub']
# ops += ['mul0', 'mul1', 'mul2']
ops += ['abs']
ops += ['sel']

comparison_ops = ['ge', 'le']

signed_ops = ['min', 'max', 'le', 'ge']

def bodysource(tests, opcode, flag_sel, lut_code):
    return f'''
    for(int i = 0; i < {len(tests)}; i++) {{
        unsigned int* test = tests[i];
        top->data0 = test[0];
        top->data1 = test[1];
        top->bit0 = test[2];
        top->bit1 = test[3];
        top->bit2 = test[4];
        top->eval();
        printf("[lut_code=%x, opcode=%x, flag_sel=%x, Test Iteration %d] Inputs: data0=%x, data1=%x, bit0=%x, bit1=%x, bit2=%x\\n", {lut_code}, {opcode}, {flag_sel}, i, test[0], test[1], test[2], test[3], test[4]);
        printf("    expected_res=%x, actual_res=%x\\n", test[5], top->res);
        printf("    expected_res_p=%x, actual_res_p=%x\\n", test[6], top->res_p);
        assert(top->res == test[5]);
        assert(top->res_p == test[6]);
    }}
'''


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
    step(top);

    top->cfg_d = {cfg_d};
    top->cfg_a = 0xFF;  // opcode
    step(top);
    step(top);
    top->cfg_en = 0;

    step(top);

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
        metafunc.parametrize("signed", [True, False])
    if 'strategy' in metafunc.fixturenames:
        metafunc.parametrize("strategy", [complete, random])

    if 'flag_sel' in metafunc.fixturenames:
        metafunc.parametrize("flag_sel", range(0, 16))

    if 'lut_code' in metafunc.fixturenames:
        metafunc.parametrize("lut_code", range(0, 16))
def test_op(strategy, op, flag_sel):
    if flag_sel == 0x14:
        return  # Skip lut, tested separately
    bit2_mode = 0x2  # BYPASS
    bit1_mode = 0x2  # BYPASS
    bit0_mode = 0x2  # BYPASS
    data1_mode = 0x2  # BYPASS
    data0_mode = 0x2  # BYPASS
    irq_en = 0
    acc_en = 0
    signed = 0
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
        n = 16
    else:
        n = 256
    tests = strategy(_op, n, 16)

    body = bodysource(tests, _op.opcode, flag_sel, lut_code)
    test = testsource(tests)

    compile_harness(f'build/sim_test_lut_{strategy.__name__}.cpp', test, body, lut_code, cfg_d)

    run_verilator_test('test_pe_unq1', f'sim_test_lut_{strategy.__name__}', 'test_pe_unq1')

# def test_lut(strategy, lut_code):
#     op = "add"
#     flag_sel = 0x14
#     bit2_mode = 0x2  # BYPASS
#     bit1_mode = 0x2  # BYPASS
#     bit0_mode = 0x2  # BYPASS
#     data1_mode = 0x2  # BYPASS
#     data0_mode = 0x2  # BYPASS
#     irq_en = 0
#     acc_en = 0
#     signed = 0
#     _op = getattr(pe, op)(flag_sel).lut(lut_code)
#     cfg_d = bit2_mode << 28 | \
#             bit1_mode << 26 | \
#             bit0_mode << 24 | \
#             data1_mode << 18 | \
#             data0_mode << 16 | \
#             flag_sel << 12 | \
#             irq_en << 10 | \
#             acc_en << 9 | \
#             signed << 6 | \
#             _op.opcode
# 
#     if strategy is complete:
#         n = 16
#     else:
#         n = 256
#     tests = strategy(_op, n, 16)
# 
#     body = bodysource(tests, _op.opcode, lut_code)
#     test = testsource(tests)
# 
#     compile_harness(f'build/sim_test_lut_{strategy.__name__}.cpp', test, body, lut_code, cfg_d)
# 
#     run_verilator_test('test_pe_unq1', f'sim_test_lut_{strategy.__name__}', 'test_pe_unq1')
