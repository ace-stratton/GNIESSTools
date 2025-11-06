import pigpio
import time

pi = pigpio.pi()
LOAD = 23
CLK  = 24
MJF = 22

bitLOAD = 1 << LOAD
bitCLK  = 1 << CLK
bitMJF = 1 << MJF

# --- Create waveform ---
pi.wave_clear()

pulses = []

pulses += [
    pigpio.pulse(bitMJF, 0,2), # high for 2 ticks (200 ns)
    pigpio.pulse(0, bitMJF,2),# low for 2 ticks (200 ns)
]
for _ in range (10):
# 1) Load pulse: low 200 ns, high 200 ns
    pulses += [
        pigpio.pulse(0, bitLOAD, 0),   # low for 2 ticks (200 ns)
        pigpio.pulse(bitLOAD, 0, 0)    # high for 2 ticks (200 ns)
    ]

# 2) 16 clock cycles at ~2.5 MHz (4 ticks per period)
    for _ in range(16):
        pulses += [
            pigpio.pulse(bitCLK, 0, 0),  # CLK high 200 ns
            pigpio.pulse(0, bitCLK, 0)   # CLK low 200 ns
        ]
    
    pulses += [
        pigpio.pulse(0, 0, 60),  # hold 60 us inbewteen
    ]

pi.wave_add_generic(pulses)
wid = pi.wave_create()

pi.wave_send_repeat(wid)


    
