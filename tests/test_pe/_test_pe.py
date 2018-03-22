import pe
from testvectors import complete, random
from verilator import testsource, run_verilator_test


ops  = ['or_', 'and_', 'xor']
# ops += ['inv']
# ops += ['lshr', 'lshl']
# ops += ['ashr']
# ops += ['add', 'sub']
# ops += ['mul0', 'mul1', 'mul2']
# ops += ['abs']
# ops += ['sel']

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
    bit2_mode = 0
    bit1_mode = 0
    bit0_mode = 0
    data1_mode = 0
    data0_mode = 0
    flag_sel = 0
    irq_en = 0
    acc_en = 0
    signed = 0
    _op = getattr(pe, op)()
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

    cfg_a = 0xFF # opcode

    if strategy is complete:
        n = 16
    else:
        n = 256
    tests = strategy(_op, n, 16)

    def bodysource(tests):
        return f'''
        for(int i = 0; i < {len(tests)}; i++) {{
            unsigned int* test = tests[i];
            top->data0 = test[0];
            top->data1 = test[1];
            // top->op_d_p = test[2];
            top->eval();
            printf("[opcode=%x, Test Iteration %d] Inputs: data0=%x, data1=%x, \\n", {_op.opcode}, i, test[0], test[1]);
            printf("    expected_res=%x, actual_res=%x\\n", test[3], top->res);
            printf("    expected_res_p=%x, actual_res_p=%x\\n", test[4], top->res_p);
            assert(top->res == test[3]);
            assert(top->res_p == test[4]);
        }}
    '''

    body = bodysource(tests)
    test = testsource(tests)

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

int main(int argc, char **argv, char **env) {{
    Verilated::commandArgs(argc, argv);
    Vtest_pe_unq1* top = new Vtest_pe_unq1;

    {test}

    top->cfg_d = {cfg_d};
    top->cfg_en = 1;
    top->cfg_a = {cfg_a};
    step(top);

    {body}

    delete top;
    printf("Success!\\n");
    exit(0);
}}
"""
    with open(f'build/sim_test_{op}_{strategy.__name__}.cpp', "w") as f:
        f.write(harness)
    run_verilator_test('test_pe_unq1', f'sim_test_{op}_{strategy.__name__}', 'test_pe_unq1')
