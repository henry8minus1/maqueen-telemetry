"""Stationary Maqueen Lite V5 + micro:bit V2 demonstration.
A pauses/resumes the lights; B advances the pattern. Motors stay stopped.
"""
from microbit import *
import telemetry as mt
import neopixel
import time
from machine import time_pulse_us

TAG = 'sensors-v1'
COLORS = [(0,0,0),(32,0,0),(0,32,0),(32,32,0),(0,0,32),(32,0,32),(0,32,32),(32,32,32)]
pixels = neopixel.NeoPixel(pin15, 4)
phase = 1
paused = False

def write(reg, *values):
    i2c.write(16, bytes([reg] + list(values)))

def range_cm():
    pin1.write_digital(0)
    time.sleep_us(2)
    pin1.write_digital(1)
    time.sleep_us(10)
    pin1.write_digital(0)
    pulse = time_pulse_us(pin2, 1, 30000)
    return int(pulse / 58) if pulse > 0 else None

def lights():
    left = phase if not paused else 0
    right = (phase + 3) % 8 if not paused else 0
    write(11, left or 8)
    write(12, right or 8)
    codes = []
    for i in range(4):
        code = (phase + i) % 8 if not paused else 0
        pixels[i] = COLORS[code]
        codes.append(str(code))
    pixels.show()
    display.show(Image('99999:99999:99999:99999:99999') if phase % 2 else Image.HEART)
    if paused:
        display.clear()
    return str(left)+str(right)+''.join(codes)

write(70, 1)
sleep(150)
write(71, 0)
write(0, 0, 0)
write(2, 0, 0)
pin16.set_pull(pin16.PULL_UP)
mt.start(1, TAG, background=False)
mt.poll_maqueen(True)
last_light = last_extra = last_range = 0
extra = 0
light_codes = lights()
ir_count = 0
ir_active = False
print('LIGHTS SENSORS DEMO', TAG)
while True:
    now = running_time()
    if button_a.was_pressed():
        paused = not paused
        light_codes = lights()
    if button_b.was_pressed() or (not paused and now-last_light > 3200):
        phase = phase % 7 + 1
        last_light = now
        light_codes = lights()
    # Raw IR activity counter, not a decoded remote key. Polling can miss pulses.
    active = pin16.read_digital() == 0
    if active and not ir_active:
        ir_count = (ir_count + 1) % 100000
    ir_active = active
    if now-last_range > 300:
        last_range = now
        mt.distance(range_cm())
    mt.status('paused' if paused else 'lights-demo', 0, 0)
    mt.poll()
    # Keep the two LED frames adjacent for the receiver's pairing check.
    if now-last_extra > 220 and mt._phase != 3:
        last_extra = now
        if extra == 0:
            mt._send('X', 'o'+light_codes)
        elif extra == 1:
            mt._send('X', 's'+str(microphone.sound_level()))
        elif extra == 2:
            mt._send('X', 't'+str(int(pin_logo.is_touched())))
        elif extra == 3:
            mt._send('X', 'i'+str(ir_count))
        elif extra == 4:
            mt._send('X', 'h'+str(compass.heading() if compass.is_calibrated() else -1))
        elif extra == 5:
            mt._send('X', 'm'+str(int(compass.get_field_strength()/1000)))
        else:
            mt._send('X', 'l'+str(display.read_light_level()))
        extra = (extra + 1) % 7
    sleep(2)
