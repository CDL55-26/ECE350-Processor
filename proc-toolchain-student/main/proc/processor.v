/**
 * READ THIS DESCRIPTION!
 *
 * This is your processor module that will contain the bulk of your code submission. You are to implement
 * a 5-stage pipelined processor in this module, accounting for hazards and implementing bypasses as
 * necessary.
 *
 * Ultimately, your processor will be tested by a master skeleton, so the
 * testbench can see which controls signal you active when. Therefore, there needs to be a way to
 * "inject" imem, dmem, and regfile interfaces from some external controller module. The skeleton
 * file, Wrapper.v, acts as a small wrapper around your processor for this purpose. Refer to Wrapper.v
 * for more details.
 *
 * As a result, this module will NOT contain the RegFile nor the memory modules. Study the inputs 
 * very carefully - the RegFile-related I/Os are merely signals to be sent to the RegFile instantiated
 * in your Wrapper module. This is the same for your memory elements. 
 *
 *
 */
module processor(
    // Control signals
    clock,                          // I: The master clock
    reset,                          // I: A reset signal

    // Imem
    address_imem,                   // O: The address of the data to get from imem
    q_imem,                         // I: The data from imem

    // Dmem
    address_dmem,                   // O: The address of the data to get or put from/to dmem
    data,                           // O: The data to write to dmem
    wren,                           // O: Write enable for dmem
    q_dmem,                         // I: The data from dmem

    // Regfile
    ctrl_writeEnable,               // O: Write enable for RegFile
    ctrl_writeReg,                  // O: Register to write to in RegFile
    ctrl_readRegA,                  // O: Register to read from port A of RegFile
    ctrl_readRegB,                  // O: Register to read from port B of RegFile
    data_writeReg,                  // O: Data to write to for RegFile
    data_readRegA,                  // I: Data from port A of RegFile
    data_readRegB                   // I: Data from port B of RegFile
	 
	);

	// Control signals
	input clock, reset;
	
	// Imem
    output [31:0] address_imem;
	input [31:0] q_imem;

	// Dmem
	output [31:0] address_dmem, data;
	output wren;
	input [31:0] q_dmem;

	// Regfile
	output ctrl_writeEnable;
	output [4:0] ctrl_writeReg, ctrl_readRegA, ctrl_readRegB;
	output [31:0] data_writeReg;
	input [31:0] data_readRegA, data_readRegB;

	/* YOUR CODE STARTS HERE */

    /*Wires*/

    //PC Wires
    wire [31:0] PC_output, PC_in, PC_adder_output;
    wire PC_adder_OVF;

    // FD Latch Wires
    wire [63:0] FD_Latch_input, FD_Latch_output;
    wire [31:0] FD_Latch_PC, FD_Latch_Instr;
    wire [16:0] FD_immediate_wire;
    wire [4:0] FD_opcode_wire, FD_rd_wire, FD_rs_wire, FD_rt_wire, FD_shamt_wire, FD_ALU_op_wire;

    // DX Latch Wires
    wire [127:0] DX_Latch_input, DX_Latch_output;
    wire [31:0] DX_Latch_PC, DX_Latch_A, DX_Latch_B, DX_Latch_Instr, DX_instruction_decoder;
    wire [16:0] DX_immediate_wire;
    wire [4:0] DX_opcode_wire, DX_rd_wire, DX_rs_wire, DX_rt_wire, DX_shamt_wire, DX_ALU_op_wire;

    // WB Latch Wires
    wire [95:0] WB_Latch_input, WB_Latch_output;
    wire [31:0] WB_Latch_PC, WB_Latch_Instr, WB_Latch_writeVal, WB_instruction_decoder;
    wire [16:0] WB_immediate_wire;
    wire [4:0] WB_opcode_wire, WB_rd_wire, WB_rs_wire, WB_rt_wire, WB_shamt_wire, WB_ALU_op_wire;
    
    // execute_ALU Wires
    wire [31:0] execute_ALU_out_wire, SEX_DX_immediate_wire, B_immediate_mux_out;
    wire [4:0] ALU_op_control;
    wire execute_isNotEqual, execute_isLessThan, execute_overflow, R_S_ALU_mux_sel;

    // Control Signals
    wire RegFile_WE, B_immediate_mux_sel;

    /*Instruction decoders and parsing*/

        //setup decoders
        assign DX_instruction_decoder = 32'b1 << DX_opcode_wire; //5bit decoder with imem output (instruction) as input
        assign WB_instruction_decoder = 32'b1 << WB_opcode_wire;

        /*FD Instruction*/
            //parse instructions
            assign FD_opcode_wire = FD_Latch_Instr[31:27];
            assign FD_rd_wire = FD_Latch_Instr[26:22];
            assign FD_rs_wire = FD_Latch_Instr[21:17];
            assign FD_rt_wire = FD_Latch_Instr[16:12];
            assign FD_shamt_wire = FD_Latch_Instr[11:7];
            assign FD_ALU_op_wire = FD_Latch_Instr[6:2];

            //immediate for i-type
            assign FD_immediate_wire = FD_Latch_Instr[16:0];

        /*DX Instruction*/
            //parse instructions
            assign DX_opcode_wire = DX_Latch_Instr[31:27];
            assign DX_rd_wire = DX_Latch_Instr[26:22];
            assign DX_rs_wire = DX_Latch_Instr[21:17];
            assign DX_rt_wire = DX_Latch_Instr[16:12];
            assign DX_shamt_wire = DX_Latch_Instr[11:7];
            assign DX_ALU_op_wire = DX_Latch_Instr[6:2];

            //immediate for i-type
            assign DX_immediate_wire = DX_Latch_Instr[16:0];


        /*WB Instructions*/
            //parse instructions
            assign WB_opcode_wire = WB_Latch_Instr[31:27];
            assign WB_rd_wire = WB_Latch_Instr[26:22];
            assign WB_rs_wire = WB_Latch_Instr[21:17];
            assign WB_rt_wire = WB_Latch_Instr[16:12];
            assign WB_shamt_wire = WB_Latch_Instr[11:7];
            assign WB_ALU_op_wire = WB_Latch_Instr[6:2];

            //immediate for i-type
            assign WB_immediate_wire = WB_Latch_Instr[16:0];



    /*Control Wires*/

        //enable reg file for opcode of 0 (alu ops) or 101 = addi
        assign RegFile_WE = WB_instruction_decoder[0] | WB_instruction_decoder[5]; //*****WILL HAVE TO CHANGE WHEN ADDING LATCHES
        
        //Choose s-extended immediate from mux if i-type
        assign B_immediate_mux_sel = DX_instruction_decoder[5]; //*****WILL HAVE TO CHANGE WHEN ADDING LATCHED

    
    /*Program Counter*/

        //setup PC
        register PC_register(PC_output, PC_in, reset, 1'b1, clock ); //rising edge, always enabled

        CLA32 PC_adder(PC_adder_output, PC_adder_OVF, PC_output, 32'b1, 1'b0); //carry in zero
        assign PC_in = PC_adder_output; //*****WILL NEED TO CHANGE***** assuming pc always = pc +1

        //Handle Ins ROM
        assign address_imem = PC_output; //imem address = current PC, not PC +1
    
    /*Pipeline Latches*/
        /* FD Latch **********************/
        //input to FD latch is the instr from imem and will be PC in up 32 bits, right now ignorning, inputting zeros
        
        assign FD_Latch_input = {PC_adder_output, q_imem}; //uper 32 bits = PC + 1, will use for control later

        register64 FD_Latch(FD_Latch_output, FD_Latch_input, reset, 1'b1, ~clock); //enable to latch always 1, falling edge reg

        assign FD_Latch_PC = FD_Latch_output[63:32];
        assign FD_Latch_Instr = FD_Latch_output[31:0];

        /* DX Latch **********************/
        //Upper 32b should be PC from FD_Latch_output, lower 32b should be instr passed from FD latch
        assign DX_Latch_input = {FD_Latch_PC, data_readRegA, data_readRegB, FD_Latch_Instr};

        //DX Latch
        register128 DX_Latch(DX_Latch_output, DX_Latch_input, reset, 1'b1, ~clock); //enable to latch always 1, falling edge reg
        assign DX_Latch_Instr = DX_Latch_output[31:0];
        assign DX_Latch_B = DX_Latch_output[63:32];
        assign DX_Latch_A = DX_Latch_output[95:64];
        assign DX_Latch_PC = DX_Latch_output[127:96];



        /* WB Latch **********************/

        assign WB_Latch_input = {DX_Latch_PC, execute_ALU_out_wire, DX_Latch_Instr};

        //WB Latch
        register96 WB_Latch(WB_Latch_output, WB_Latch_input, reset, 1'b1, ~clock); //enable to latch always 1, falling edge reg
        assign WB_Latch_PC = WB_Latch_output[95:64];
        assign WB_Latch_writeVal = WB_Latch_output[63:32];
        assign WB_Latch_Instr = WB_Latch_output[31:0];
        
    
    /*Register File Handling*/

        assign ctrl_writeEnable = RegFile_WE; //WE determined by DX instr *****WILL HAVE TO CHANGE TO UPDATE LATCH
        assign ctrl_writeReg = WB_rd_wire; //writing to register determined by DX latch instr ****WILL HAVE TO CHANGE IN FUTURE***
        assign ctrl_readRegA = FD_rs_wire; //reading from FD rs
        assign ctrl_readRegB = FD_rt_wire; //reading from FD rt
        assign data_writeReg = WB_Latch_writeVal; //data to write to the register

    /*ALU Handling*/

        assign SEX_DX_immediate_wire = { {15{DX_immediate_wire[16]}}, DX_immediate_wire }; //sign extend the immediate
        mux_2 B_immediate_mux(B_immediate_mux_out, B_immediate_mux_sel, DX_Latch_B, SEX_DX_immediate_wire); //if control is 1 (i-type), choose SEX option

        assign R_S_ALU_mux_sel = (DX_opcode_wire == 5'b0); //if the opcode is all zeros, its an R-type, set 1
        mux_2_5bit R_S_ALU_mux(ALU_op_control, R_S_ALU_mux_sel, 5'b0, DX_ALU_op_wire );//if opcode == 0, I-type, only add

        alu execute_ALU(DX_Latch_A, B_immediate_mux_out, ALU_op_control, DX_shamt_wire, execute_ALU_out_wire, execute_isNotEqual, execute_isLessThan, execute_overflow);

	/* END CODE */

endmodule
