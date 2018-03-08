import pytest
import subprocess
import pe
from testvectors import complete
from verilator import compile, run_verilator_test

ops  = ['or_', 'and_', 'xor']
# ops += ['inv']
ops += ['lshr', 'lshl']
# ops += ['ashr']
ops += ['add', 'sub']
ops += ['abs']
ops += ['eq']
ops += ['sel']

signed_ops = ['min', 'max', 'le', 'ge']
def pytest_generate_tests(metafunc):
    if 'op' in metafunc.fixturenames:
        metafunc.parametrize("op", ops)
    if 'signed_op' in metafunc.fixturenames:
        metafunc.parametrize("signed_op", signed_ops)
        metafunc.parametrize("signed", [True, False])
    if 'const_value' in metafunc.fixturenames:
        metafunc.parametrize("const_value", range(16))

def test_op(op):
    a = getattr(pe, op)()

    tests = complete(a, 4, 16)

    compile(f'test_{op}_complete', 'test_pe_comp_unq1', a.opcode, tests)
    run_verilator_test('test_pe_comp_unq1', f'sim_test_{op}_complete', 'test_pe_comp_unq1')

def test_signed_op(signed_op, signed):
    a = getattr(pe, signed_op)(signed)

    tests = complete(a, 4, 16)

    compile(f'test_{signed_op}_complete', 'test_pe_comp_unq1', a.opcode, tests)
    run_verilator_test('test_pe_comp_unq1', f'sim_test_{signed_op}_complete', 'test_pe_comp_unq1')

@pytest.mark.skip
def test_const(const_value):
    a = pe.const(const_value)

    tests = complete(a, 4, 16)

    compile(f'test_const_complete', 'test_pe_comp_unq1', a.opcode, tests)
    run_verilator_test('test_pe_comp_unq1', f'sim_test_const_complete', 'test_pe_comp_unq1')
