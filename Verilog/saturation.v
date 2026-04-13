// ============================================================
//  Saturation  —  32-bit signed → 16-bit signed
//  Clamps result to [-32768, +32767]
// ============================================================
module saturation (
    input  wire signed [31:0] in,
    output reg  signed [15:0] out
);
    always @(*) begin
        if      (in > 32'sh00007FFF) out = 16'sh7FFF;   // +32767
        else if (in < 32'shFFFF8000) out = 16'sh8000;   // -32768
        else                          out = in[15:0];
    end
endmodule