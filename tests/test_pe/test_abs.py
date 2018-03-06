import subprocess
from pe import abs
from testvectors import complete
from verilator import compile

def test_abs():
    a = abs()

    tests = complete(a, 4, 16)
    print("===== BEGIN: Compiling verilator test harness ==========")
    compile('test_pe_comp_unq1',a.opcode,tests)
    print("===== DONE:  Compiling verilator test harness ==========")
    print("===== BEGIN: Using verilator to generate test files =====")
    assert not subprocess.call("verilator -I../rtl -Wno-fatal --cc test_pe_comp_unq1 --exe sim_test_pe_comp_unq1.cpp", shell=True, cwd="build")
    print("===== DONE:  Using verilator to generate test files =====")
    print("===== BEGIN: Compiling verilator test ===================")
    assert not subprocess.call("make -C obj_dir -j -f Vtest_pe_comp_unq1.mk Vtest_pe_comp_unq1", shell=True, cwd="build")
    print("===== DONE:  Compiling verilator test ===================")
    print("===== BEGIN: Running verilator test =====================")
    assert not subprocess.call("./obj_dir/Vtest_pe_comp_unq1", shell=True, cwd="build")
    print("===== DONE:  Running verilator test =====================")

