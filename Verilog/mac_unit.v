// ============================================================
//  MAC Unit  —  one Multiply step
//  Outputs the RAW 32-bit product from Booth's multiplier.
//  Saturation is NOT applied here — it belongs on the final sum
//  in fir_filter.v, not on each individual product.
// ============================================================
module mac_unit (
    input  wire        clk,
    input  wire        rst,
    input  wire        start,
    input  wire signed [15:0] A,
    input  wire signed [15:0] B,
    output wire signed [31:0] product_out,   // RAW 32-bit (no saturation)
    output wire               done
);

    booth_multiplier u_mult (
        .clk     (clk),
        .rst     (rst),
        .start   (start),
        .A       (A),
        .B       (B),
        .product (product_out),
        .done    (done)
    );

endmodule