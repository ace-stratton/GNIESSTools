#!/usr/bin/env python3
import pigpio
import time
import sys

# ========= CONFIGURATION =========
DATA_PIN = 25     # BCM number for the TX data line (CHANGE TO YOUR PIN)
CLK_PIN = 24      # BCM 24: existing clock signal (driven elsewhere)
LOAD_PIN = 23     # BCM 23: existing load pulse (active LOW, driven elsewhere)

BITS_PER_WORD = 16
WORDS_PER_FRAME = 10           # if you know it's always 10
SYNC_WORD = 0xD00D             # expected 10th word
MSB_FIRST = True               # set False if your data is LSB-first
# ================================

class SerialWordDecoder:
    def __init__(self, pi):
        self.pi = pi

        # Internal state
        self.current_word = 0
        self.bit_count = 0
        self.word_index = 0   # 0-based index within frame

        # ---- IMPORTANT: Only touch the DATA pin config ----
        self.pi.set_mode(DATA_PIN, pigpio.INPUT)
        self.pi.set_pull_up_down(DATA_PIN, pigpio.PUD_OFF)

        # DO NOT touch mode or pulls on CLK/LOAD.
        # They are driven by another script using pigpio.

        # Callbacks:
        #  - clock rising edge: sample a bit
        #  - load falling edge: start of new frame
        self.clk_cb = self.pi.callback(
            CLK_PIN, pigpio.RISING_EDGE, self._on_clk_rising
        )
        self.load_cb = self.pi.callback(
            LOAD_PIN, pigpio.FALLING_EDGE, self._on_load_falling
        )

    def _on_load_falling(self, gpio, level, tick):
        """
        LOAD is active low. When we see a falling edge, treat it as
        the start of a new frame.
        """
        self.current_word = 0
        self.bit_count = 0
        self.word_index = 0

        print("\n==== New frame detected (LOAD went low) ====")

    def _on_clk_rising(self, gpio, level, tick):
        """
        On each clock rising edge, sample the DATA pin and shift into the
        current 16-bit word.
        """
        bit = self.pi.read(DATA_PIN) & 0x1

        if MSB_FIRST:
            # Shift left, OR in bit as the LSB
            self.current_word = ((self.current_word << 1) | bit) & 0xFFFF
        else:
            # LSB-first: shift right, OR in bit as MSB
            self.current_word = ((self.current_word >> 1) | (bit << 15)) & 0xFFFF

        self.bit_count += 1

        if self.bit_count >= BITS_PER_WORD:
            word_value = self.current_word

            print(f"Word {self.word_index:2d}: 0x{word_value:04X}  ({word_value:5d})")

            # Check if this is the 10th word (index 9)
            if self.word_index == 9:
                if word_value == SYNC_WORD:
                    print("  -> 10th word OK (0xD00D)")
                else:
                    print(f"  -> WARNING: 10th word != 0xD00D (got 0x{word_value:04X})")

            # Prepare for next word
            self.word_index += 1
            self.bit_count = 0
            self.current_word = 0

            if self.word_index >= WORDS_PER_FRAME:
                print("==== End of frame (10 words) ====")

    def stop(self):
        self.clk_cb.cancel()
        self.load_cb.cancel()


def main():
    pi = pigpio.pi()
    if not pi.connected:
        print("Failed to connect to pigpio daemon. Did you run `sudo pigpiod`?")
        sys.exit(1)

    decoder = SerialWordDecoder(pi)

    print("Listening for serial words (read-only on LOAD/CLK)...")
    print(f"  DATA  pin (BCM): {DATA_PIN}  (configured as INPUT)")
    print(f"  CLK   pin (BCM): {CLK_PIN}  (left alone, driven by other script)")
    print(f"  LOAD  pin (BCM): {LOAD_PIN} (left alone, driven by other script)")
    print("Press Ctrl+C to exit.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        decoder.stop()
        pi.stop()


if __name__ == "__main__":
    main()
