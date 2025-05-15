import numpy as np
from gnuradio import gr
import time

class BWFillRepeater(gr.sync_block):
    """Repeats each complex input sample N times to fill the output bandwidth by frequency shifting."""

    def __init__(self, input_bw=12e3, output_bw=20e6, samp_rate=1.0):
        """Initializes the BW Fill Repeater block.
        
        Arguments:
        input_bw -- Bandwidth of the input signal in Hz (default: 12e3).
        output_bw -- Target output bandwidth in Hz (default: 20e6).
        samp_rate -- Sample rate in Hz (default: 1.0).
        """
        gr.sync_block.__init__(
            self,
            name='BW Fill Repeater',
            in_sig=[np.complex64],  # Complex input signal
            out_sig=[np.complex64]  # Complex output signal
        )
        
        self.input_bw = input_bw
        self.output_bw = output_bw
        self.samp_rate = samp_rate
        
        # Calculate the number of frequency-shifted copies needed
        self.num_copies = max(1, int(self.output_bw // self.input_bw))
        self.shift_spacing = self.output_bw / self.num_copies
        self.sample_idx = 0  # Track the time for mixing

    def set_input_bandwidth(self, input_bw):
        """Updates the input bandwidth and recalculates necessary parameters."""
        if input_bw > 0:
            self.input_bw = input_bw
            self.num_copies = max(1, int(self.output_bw // self.input_bw))
            self.shift_spacing = self.output_bw / self.num_copies
            print(f"Input bandwidth updated: {self.input_bw:.2f} Hz, Num Copies: {self.num_copies}, Shift Spacing: {self.shift_spacing:.2f} Hz")

    def work(self, input_items, output_items):
        """Processes input samples and outputs frequency-shifted samples."""
        in0 = input_items[0]
        out = output_items[0]
        
        num_samples = len(in0)
        out[:] = np.zeros(num_samples, dtype=np.complex64)  # Initialize output buffer

        # Time vector for signal processing
        t = np.arange(self.sample_idx, self.sample_idx + num_samples) / self.samp_rate

        # Frequency shift over the specified number of copies
        for i in range(self.num_copies):
            # Frequency shift for this copy
            freq_shift = -self.output_bw / 1 + i * self.shift_spacing
            
            # Create the frequency mixer for this copy
            mixer = np.exp(2j * np.pi * freq_shift * t).astype(np.complex64)
            
            # Apply the frequency shift to the input signal
            out += in0 * mixer

        # Normalize output to avoid boosting power
        #out[:] /= self.num_copies
        

        # Update sample index for the next processing step
        self.sample_idx += num_samples

        # Return the number of output samples processed
        return len(out)
