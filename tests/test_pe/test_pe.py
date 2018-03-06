import subprocess
from pe import abs, and_
from testvectors import complete
from verilator import compile, run_verilator_test

def test_abs():
    a = abs()

    tests = complete(a, 4, 16)

    compile('test_abs_complete', 'test_pe_comp_unq1', a.opcode, tests)
    run_verilator_test('test_pe_comp_unq1', 'sim_test_abs_complete', 'test_pe_comp_unq1')

def test_and():
    a = and_()

    tests = complete(a, 4, 16)
    compile('test_and_complete', 'test_pe_comp_unq1', a.opcode, tests)
    run_verilator_test('test_pe_comp_unq1', 'sim_test_and_complete', 'test_pe_comp_unq1')
