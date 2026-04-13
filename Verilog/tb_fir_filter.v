`timescale 1ns/1ps
// ============================================================
//  Testbench — handles ANY audio file size automatically.
//
//  N_SAMPLES is injected at compile time by run_sim.py:
//    iverilog -DN_SAMPLES=<count> ...
//  Default fallback = 65536 if not set (covers most files).
//  No more "Too many words" warning.
// ============================================================
`ifndef N_SAMPLES
  `define N_SAMPLES 65536
`endif

module tb_fir_filter;

    reg         clk, rst, valid_in;
    reg  signed [15:0] x_in;
    wire signed [15:0] y_out;
    wire        valid_out;

    // Array sized EXACTLY to the audio file
    reg [15:0] samples [0:`N_SAMPLES-1];
    integer i, out_file, timeout;

    fir_filter uut (
        .clk      (clk),
        .rst      (rst),
        .valid_in (valid_in),
        .x_in     (x_in),
        .y_out    (y_out),
        .valid_out(valid_out)
    );

    always #5 clk = ~clk;

    initial begin
        $readmemh("Output/audio_samples.hex", samples);
        out_file = $fopen("Output/verilog_output.txt", "w");

        clk = 0; rst = 1; valid_in = 0; x_in = 0;
        #20; rst = 0; #10;

        for (i = 0; i < `N_SAMPLES; i = i + 1) begin
            @(posedge clk); #1;
            x_in     = $signed(samples[i]);
            valid_in = 1;
            @(posedge clk); #1;
            valid_in = 0;

            timeout = 0;
            while (!valid_out && timeout < 100) begin
                @(posedge clk);
                timeout = timeout + 1;
            end

            if (timeout >= 100) begin
                $display("ERROR: Timeout at sample %0d", i);
                $fclose(out_file);
                $finish;
            end

            $fdisplay(out_file, "%0d", $signed(y_out));
        end

        $fclose(out_file);
        $display("Done. %0d samples → Output/verilog_output.txt", `N_SAMPLES);
        $finish;
    end

endmodule