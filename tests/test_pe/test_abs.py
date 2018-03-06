import subprocess
from pe import abs
from testvectors import complete
from verilator import compile, run_verilator_test

def test_abs():
    a = abs()

    tests = complete(a, 4, 16)

    compile('test_abs_complete', 'test_pe_comp_unq1', a.opcode,tests)
    run_verilator_test('test_pe_comp_unq1', 'sim_test_abs_complete', 'test_pe_comp_unq1')
