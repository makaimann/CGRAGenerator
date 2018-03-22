import pytest
import os
import subprocess
import inspect
from bit_vector import BitVector

__all__ = ['harness', 'compile']

def to_string(val):
    if isinstance(val, bool) or isinstance(val, BitVector) and val.num_bits == 1:
        return "1" if val else "0"
    else:
        return str(val)

@pytest.mark.skip("Not a test")
def testsource(tests):
    source = '''
    unsigned int tests[{}][{}] = {{
'''.format(len(tests), len(tests[0]))

    for test in tests:
        testvector = ', '.join([to_string(t) for t in test])
        source += '''\
        {{ {} }}, 
'''.format(testvector)

    source += '''\
    };
'''
    return source

def bodysource(tests):
    return '''
    for(int i = 0; i < {ntests}; i++) {{
        unsigned int* test = tests[i];
        top->op_a = test[0];
        top->op_b = test[1];
        top->op_d_p = test[2];
        top->eval();
        printf("[opcode=%x, Test Iteration %d] Inputs: op_a=%x, op_b=%x, op_d_p=%x\\n", top->op_code, i, test[0], test[1], test[2]);
        printf("    expected_res=%x, actual_res=%x\\n", test[3], top->res);
        printf("    expected_res_p=%x, actual_res_p=%x\\n", test[4], top->res_p);
        assert(top->res == test[3]);
        assert(top->res_p == test[4]);
    }}
'''.format(ntests=len(tests))

def harness(top_name, opcode, tests):

    test = testsource(tests)
    body = bodysource(tests)
    return '''\
#include "V{top_name}.h"
#include "verilated.h"
#include <cassert>
#include <iostream>
#include <printf.h>

int main(int argc, char **argv, char **env) {{
    Verilated::commandArgs(argc, argv);
    V{top_name}* top = new V{top_name};

    {test}

    top->op_code = {op};

    {body}

    delete top;
    std::cout << "Success" << std::endl;
    exit(0);
}}'''.format(test=test,body=body,top_name=top_name,op=opcode&0x1ff)


def compile(name, top_name, opcode, tests):
    # print("========== BEGIN: Compiling verilator test harness ===========")
    verilatorcpp = harness(top_name, opcode, tests)
    with open('build/sim_'+name+'.cpp', "w") as f:
        f.write(verilatorcpp)
    # print("========== DONE:  Compiling verilator test harness ===========")



def run_verilator_test(verilog_file_name, driver_name, top_module):
    (_, filename, _, _, _, _) = inspect.getouterframes(inspect.currentframe())[1]
    file_path = os.path.dirname(filename)
    build_dir = os.path.join(file_path, 'build')
    # print("========== BEGIN: Using verilator to generate test files =====")
    assert not subprocess.call('verilator -I../rtl -Wno-fatal --cc {} --exe {}.cpp --top-module {}'.format(verilog_file_name, driver_name, top_module), cwd=build_dir, shell=True)
    # print("========== DONE:  Using verilator to generate test files =====")
    # print("========== BEGIN: Compiling verilator test ===================")
    assert not subprocess.call('make --silent -C obj_dir -j -f V{0}.mk V{0} -B'.format(top_module), cwd=build_dir, shell=True)
    # print("========== DONE:  Compiling verilator test ===================")
    # print("========== BEGIN: Running verilator test =====================")
    assert not subprocess.call('./obj_dir/V{}'.format(top_module), cwd=build_dir, shell=True)
    # print("========== DONE:  Running verilator test =====================")
