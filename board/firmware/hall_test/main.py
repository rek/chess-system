# Single SS443R Hall sensor test for the Raspberry Pi Pico (MicroPython).
#
# Wiring (sensor's printed face toward you, legs down, left to right):
#   leg 1 (supply) -> Pico VBUS (pin 40, 5 V from USB)
#   leg 2 (ground) -> Pico GND  (pin 38)
#   leg 3 (output) -> Pico GP15 (pin 20), plus a 10k resistor from GP15 to 3V3(OUT) (pin 36)
# The output only pulls LOW, so the pull-up must go to 3.3 V, never 5 V.
#
# Prints MAGNET / clear every time the sensor changes, and blinks the Pico's LED with it.

from machine import Pin
import time

sensor = Pin(15, Pin.IN, Pin.PULL_UP)   # internal pull-up too, so it works without the 10k
led = Pin("LED", Pin.OUT)

last = None
changes = 0
print("Hall test running. Bring the magnet to the printed face of the sensor.")
while True:
    magnet = sensor.value() == 0        # output goes LOW when a magnet is detected
    if magnet != last:
        if last is not None:
            changes += 1
        print("{:>8} ms  {}  (changes: {})".format(
            time.ticks_ms(), "MAGNET" if magnet else "clear ", changes))
        led.value(magnet)
        last = magnet
    time.sleep_ms(5)
