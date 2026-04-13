`timescale 1ns/1ps
module booth_multiplier (
    input  wire        clk,
    input  wire        rst,
    input  wire        start,
    input  wire signed [15:0] A,
    input  wire signed [15:0] B,
    output reg  signed [31:0] product,
    output reg                done
);
    // State machine
    localparam IDLE  = 2'd0;
    localparam LOAD  = 2'd1;
    localparam RUN   = 2'd2;
    localparam DONE  = 2'd3;

    reg [1:0]        state;
    reg signed [16:0] P;     // 17-bit accumulator
    reg        [15:0] Q;     // multiplier register
    reg               Qp;    // q_{-1}
    reg signed [15:0] M;     // multiplicand
    reg        [4:0]  cnt;

    wire signed [16:0] P_next;
    assign P_next = ({Q[0],Qp}==2'b01) ? (P + {{1{M[15]}},M}) :
                    ({Q[0],Qp}==2'b10) ? (P - {{1{M[15]}},M}) :
                                          P;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            state <= IDLE; P<=0; Q<=0; Qp<=0; M<=0; cnt<=0; done<=0; product<=0;
        end else begin
            done <= 0;
            case (state)
                IDLE: begin
                    if (start) begin
                        P     <= 17'sd0;
                        Q     <= B;
                        Qp    <= 1'b0;
                        M     <= A;
                        cnt   <= 5'd0;
                        state <= RUN;
                    end
                end
                RUN: begin
                    // Arithmetic right-shift {P_next, Q, Qp} as one big register
                    P   <= P_next >>> 1;
                    Q   <= {P_next[0], Q[15:1]};
                    Qp  <= Q[0];
                    cnt <= cnt + 1;
                    if (cnt == 5'd15) begin
                        state   <= DONE;
                        // product = upper 32 bits of {P_next>>>1, shifted_Q}
                        // = {P_next[16:1], Q[15:1], Q[0]}  (before Q shifts)
                        // After shift: P becomes P_next>>>1, Q becomes {P_next[0],Q[15:1]}
                        // So 32-bit result = {(P_next>>>1)[15:0], {P_next[0],Q[15:1]}}
                        //                  = {P_next[16:1], P_next[0], Q[15:1]}
                        //                  = P_next[16:0] & Q[15:1]  (33+15=48? no)
                        // Correct: after 16 steps, full result = {P[15:0], Q[15:0]}
                        // but we haven't registered yet — use P_next>>>1 and new Q
                        product <= { P_next[16:1], {P_next[0], Q[15:1]} };
                    end
                end
                DONE: begin
                    done  <= 1'b1;
                    state <= IDLE;
                end
            endcase
        end
    end
endmodule