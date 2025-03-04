module control(
    input [4:0] FD_opcode_wire, DX_opcode_wire, XM_opcode_wire, WB_opcode_wire,
    input [4:0] DX_rd_wire, DX_rs_wire,
    output PC_ctrl_mux_select, B_J_mux_select, T_rd_mux_select,
    output rs_rstate_mux_select, rs_rd_mux_select, rt_rs_mux_select,
    output [4:0] DX_opcode_OR,
    output B_Imm_mux_select, ALU_op_mux,
    output RAM_WE,
    output X_D_mux_select, jal_setx_mux_select, WB_mux_select,
    output WB_T_PC1_mux_select, WB_xm_ctrl_mux_select, Reg_WE
);

    /*Wires*/

        // Decoder Wires
        wire [31:0] FD_instruction_decoder, DX_instruction_decoder, XM_instruction_decoder, WB_instruction_decoder;

    
    // Decoders
    assign FD_instruction_decoder = 32'b1 << FD_opcode_wire;
    assign DX_instruction_decoder = 32'b1 << DX_opcode_wire; // 5-bit decoder with imem output (instruction) as input
    assign XM_instruction_decoder = 32'b1 << XM_opcode_wire;
    assign WB_instruction_decoder = 32'b1 << WB_opcode_wire;

    //Control Bits
        //1 if a jump or branch
        assign PC_ctrl_mux_select = (DX_instruction_decoder[1] | DX_instruction_decoder[2] | DX_instruction_decoder[3] | DX_instruction_decoder[4] | DX_instruction_decoder[6]);

        //1 if branch 
        assign B_J_mux_select = (DX_instruction_decoder[2] | DX_instruction_decoder[6]);
        
        //1 if jr instr 
        assign T_rd_mux_select = DX_instruction_decoder[4];

    // Decode Bits
        //1 if bex T instr -> will read reg 30 into RS 
        assign rs_rstate_mux_select = FD_instruction_decoder[22];

        //1 if a branch instruction -> will align rd and rs with rs and rt ports of reg
        assign rs_rd_mux_select = (FD_instruction_decoder[4] | FD_instruction_decoder[6]);
        assign rt_rs_mux_select = (FD_instruction_decoder[4] | FD_instruction_decoder[6]);

    //Execute Bits
        assign DX_opcode_OR = |DX_opcode_wire[4:0]; 

        //1 if an I type instr, will be zero for R types
        assign B_Imm_mux_select = DX_opcode_OR; 
        //1 if I type, should always cause ALU to add
        assign ALU_op_mux = DX_opcode_OR;
    
    //Memory Bits
        // 1 if sw instr
        assign RAM_WE = XM_instruction_decoder[7];

    //Write Back Bits
        //1 if LW, else take execute
        assign X_D_mux_select = WB_instruction_decoder[8]; 

        //1 if JAL instr -> writing to reg 30
        assign jal_setx_mux_select = WB_instruction_decoder[3];

        //1 if JAL or setx
        assign WB_mux_select = (WB_instruction_decoder[3] | WB_instruction_decoder[21]);

        //1 if setx instr
        assign WB_T_PC1_mux_select = WB_instruction_decoder[21];

        //1 if JAL or setx
        assign WB_xm_ctrl_mux_select = (WB_instruction_decoder[21] | WB_instruction_decoder[3]);

        //Reg WE if not these -> sw, j, bne, jr, blt, bext
        assign Reg_WE = ~(WB_instruction_decoder[7] | WB_instruction_decoder[1] | WB_instruction_decoder[2] | WB_instruction_decoder[4] | WB_instruction_decoder[6] | WB_instruction_decoder[22]);

endmodule
