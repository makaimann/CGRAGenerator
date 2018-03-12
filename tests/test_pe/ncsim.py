def compile(name, opcode, tests):
    test_string = ""

    for test in tests:
        test_string += f"  op_a = {test[0]};\n"
        test_string += f"  op_b = {test[1]};\n"
        test_string += f"  assert (res  == {test[2]}) else $error(\"Failed!\");\n"

    harness = """\
`timescale 1ns/1ns
module tb;
localparam WIDTH = 16;
wire [WIDTH-1:0] op_a;
wire [WIDTH-1:0] op_b;
wire [WIDTH-1:0] op_c;
wire [WIDTH-1:0] res;

initial begin
{tests}
  #1000 $stop;
end


test_pe_comp_unq1 dut (
    .op_a(op_a),
    .op_b(op_b),
    .op_c(op_c),
    .res(res)
    .op_code({opcode});
   );
endmodule
""".format(tests=test_string,opcode=opcode&0x1ff)
    with open('build/ncsim_'+name+'_tb.v', "w") as f:
        f.write(harness)
