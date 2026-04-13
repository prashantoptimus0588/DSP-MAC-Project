`timescale 1ns/1ps
// ============================================================
//  3-Tap FIR Filter
//  y[n] = sat16( (x[n]*1 + x[n-1]*2 + x[n-2]*1) >> 2 )
// ============================================================
module fir_filter (
    input  wire        clk,
    input  wire        rst,
    input  wire        valid_in,
    input  wire signed [15:0] x_in,
    output reg  signed [15:0] y_out,
    output reg         valid_out
);
    parameter signed [15:0] B0 = 16'sd1;
    parameter signed [15:0] B1 = 16'sd2;
    parameter signed [15:0] B2 = 16'sd1;

    reg signed [15:0] x0, x1, x2;

    wire signed [31:0] mac0_out, mac1_out, mac2_out;
    wire               mac0_done, mac1_done, mac2_done;
    reg                mac_start;

    // Use 34-bit signed for sum (3x 32-bit products, no overflow)
    reg signed [33:0] sum_reg;

    mac_unit u_mac0 (.clk(clk),.rst(rst),.start(mac_start),.A(x0),.B(B0),.product_out(mac0_out),.done(mac0_done));
    mac_unit u_mac1 (.clk(clk),.rst(rst),.start(mac_start),.A(x1),.B(B1),.product_out(mac1_out),.done(mac1_done));
    mac_unit u_mac2 (.clk(clk),.rst(rst),.start(mac_start),.A(x2),.B(B2),.product_out(mac2_out),.done(mac2_done));

    // Sign-extend each 32-bit product to 34-bit and sum
    wire signed [33:0] p0 = {{2{mac0_out[31]}}, mac0_out};
    wire signed [33:0] p1 = {{2{mac1_out[31]}}, mac1_out};
    wire signed [33:0] p2 = {{2{mac2_out[31]}}, mac2_out};
    wire signed [33:0] psum = p0 + p1 + p2;
    wire signed [33:0] psum_shifted = psum >>> 2;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            x0 <= 0; x1 <= 0; x2 <= 0;
            y_out <= 0; valid_out <= 0; mac_start <= 0;
        end else begin
            mac_start <= 0;
            valid_out <= 0;

            if (valid_in) begin
                x2 <= x1; x1 <= x0; x0 <= x_in;
                mac_start <= 1;
            end

            if (mac0_done && mac1_done && mac2_done) begin
                // Saturate to 16-bit signed
                if      (psum_shifted > 34'sh0007FFF) y_out <= 16'sh7FFF;
                else if (psum_shifted < -34'sh0008000) y_out <= 16'sh8000;
                else                                    y_out <= psum_shifted[15:0];
                valid_out <= 1;
            end
        end
    end
endmodule