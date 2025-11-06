import pigpio

pi = pigpio.pi()
LOAD_PIN = 22

pi.set_mode(LOAD_PIN, pigpio.OUTPUT)
pi.wave_clear()

wf = [
    pigpio.pulse(0, 1 << LOAD_PIN, 2),  # drive LOW for 2 µs
    pigpio.pulse(1 << LOAD_PIN, 0, 0),  # back HIGH (0 µs hold)
]

pi.wave_add_generic(wf)
wave_id = pi.wave_create()

pi.wave_send_once(wave_id)
while pi.wave_tx_busy():
    pass

pi.wave_delete(wave_id)
pi.stop()