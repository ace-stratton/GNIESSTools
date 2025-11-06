import spidev
import RPi.GPIO as GPIO
import time

# --- Pin Configuration ---
SPI_BUS, SPI_DEV = 0, 0
LOAD_PIN = 22  # choose a GPIO you wired to LOAD+ (through LVDS/RS422 driver)

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(LOAD_PIN, GPIO.OUT, initial=GPIO.HIGH)

# --- SPI Setup ---
spi = spidev.SpiDev()
spi.open(SPI_BUS, SPI_DEV)
spi.max_speed_hz = 2400000     # 2.5 MHz clock
spi.mode = 0                  
spi.bits_per_word = 8
spi.no_cs = True                 # manual LOAD control

# --- Parameters ---
CLOCK_PERIOD = 0.417e-6
T_PULSE_US = CLOCK_PERIOD/2     # LOAD low time
T_SETUP_US = CLOCK_PERIOD/2     # delay after LOAD high before first clock



def receive_16bits():
    """Generate a load pulse, then read 16 bits (2 bytes) from SPI slave."""
    # LOAD active low pulse
    GPIO.output(LOAD_PIN, GPIO.LOW)
    time.sleep(T_PULSE_US )
    GPIO.output(LOAD_PIN, GPIO.HIGH)
    time.sleep(T_SETUP_US )

    # Clock in 16 bits (2 bytes)
    rx_bytes = spi.xfer2([0, 0]) # Will send out zeros, while same time receiving 2 bytes, 16 bit. Stoopid design 

    # Combine two bytes into one 16-bit word
    value = (rx_bytes[0] << 8) | rx_bytes[1]
    return value

try:
    while True:
        data = receive_16bits()
        print(f"Received: 0x{data:04X}")
        time.sleep(0.00006)  # 60us between samples
finally:
    spi.close()
    GPIO.cleanup()