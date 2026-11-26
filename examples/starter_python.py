# Single-file classroom starter. Generated from python/telemetry.py.
"""Maqueen telemetry 1.0.0. V2 run_every scheduler, or explicit poll() fallback.
Never resets the board, changes LEDs, reads button events, or commands motors.
"""
import microbit as mb
import radio
mt_VERSION = '1.0.0'
mt__robot = 1
mt__tag = 'starter'
mt__seq = 0
mt__phase = -1
mt__enabled = False
mt__scheduled = False
mt__period = 200
mt__last = 0
mt__sensors = False
mt__mode = 'idle'
mt__commands = (0, 0)
mt__cm = -1
mt__errors = 0

def mt__clean(value):
    return ''.join((c for c in str(value) if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.'))[:13] or 'starter'

def mt__send(kind, value):
    global mt__seq
    mt__seq = mt__seq + 1 & 255
    payload = str(value)
    if len(payload) > 13:
        return
    radio.send_bytes(('MT%d%s%02x%s' % (mt__robot, kind, mt__seq, payload)).encode('ascii'))

def mt__read(reg, count=1):
    mb.i2c.write(16, bytes([reg]))
    return int.from_bytes(mb.i2c.read(16, count), 'big')

def mt__tick():
    global mt__phase, mt__errors
    if not mt__enabled:
        return
    mt__phase = (mt__phase + 1) % 12
    try:
        if mt__phase == 0:
            mt__send('H', mt_VERSION + '|python')
        elif mt__phase == 1:
            mt__send('N', mt__tag)
        elif mt__phase == 2:
            mt__send('B', '%d%d' % (mb.button_a.is_pressed(), mb.button_b.is_pressed()))
        elif mt__phase in (3, 4):
            mt_start, end = (0, 13) if mt__phase == 3 else (13, 25)
            mt__send('U' if mt__phase == 3 else 'V', ''.join((str(mb.display.get_pixel(i % 5, i // 5)) for i in range(mt_start, end))))
        elif mt__phase == 5:
            mt__send('A', '%d,%d' % (mb.accelerometer.get_x(), mb.accelerometer.get_y()))
        elif mt__phase == 6:
            mt__send('Z', mb.accelerometer.get_z())
        elif mt__phase == 7:
            mt__send('T', mb.temperature())
        elif mt__phase == 8:
            mt__send('M', mt__mode)
        elif mt__phase == 9:
            mt__send('C', '%d,%d' % mt__commands)
        elif mt__phase == 10:
            mt__send('D', mt__cm)
        elif mt__phase == 11:
            mt__send('Q', int(mt__sensors))
        if mt__sensors:
            if mt__phase == 0:
                mt__send('L', mt__read(29) & 7)
            elif mt__phase == 1:
                mt__send('E', '%d,%d' % (mt__read(32, 2), mt__read(34, 2)))
            elif mt__phase == 2:
                mt__send('F', mt__read(36, 2))
            elif mt__phase == 6:
                mt__send('I', '%d,%d' % (mt__read(41, 2), mt__read(43, 2)))
            elif mt__phase == 7:
                mt__send('K', mt__read(46))
    except Exception:
        mt__errors += 1

def mt_start(robot_id=1, program_tag='starter', background=True):
    """Returns background/manual. Repeated calls do not duplicate scheduled tasks."""
    global mt__robot, mt__tag, mt__enabled, mt__scheduled, mt__period
    if robot_id not in (1, 2, 3, 4):
        raise ValueError('robot_id must be 1-4')
    mt__robot, mt__tag = (robot_id, mt__clean(program_tag))
    radio.config(group=83, channel=17, address=1969383796, length=32, queue=4, power=6)
    radio.on()
    mt__period = 180 + robot_id * 7
    mt__enabled = True
    scheduler = getattr(mb, 'run_every', None)
    if background and scheduler is not None and (not mt__scheduled):
        scheduler(mt__tick, ms=mt__period)
        mt__scheduled = True
    return 'background' if mt__scheduled else 'manual'

def mt_poll():
    """Call each iteration if start() returns manual; harmless when scheduled."""
    global mt__last
    now = mb.running_time()
    if not mt__scheduled and now - mt__last >= mt__period:
        mt__last = now
        mt__tick()

def mt_poll_maqueen(enabled=True):
    global mt__sensors
    mt__sensors = bool(enabled)

def mt_status(mode='idle', left=0, right=0):
    """Application-reported commands, not wheel feedback. Never drives motors."""
    global mt__mode, mt__commands
    mt__mode = mt__clean(mode)
    mt__commands = (max(-255, min(255, int(left))), max(-255, min(255, int(right))))

def mt_distance(cm):
    global mt__cm
    mt__cm = int(cm) if cm is not None else -1

def mt_stop():
    global mt__enabled
    mt__enabled = False

def mt_errors():
    return mt__errors

# STUDENT PROGRAM: change ID and lesson tag, then add your code below.
from microbit import *
mt_start(1, 'lesson1-v1')
display.show(Image.HAPPY)
while True:
    if button_a.was_pressed():
        display.show('A')
        mt_status('button-a')
    if button_b.was_pressed():
        display.show('B')
        mt_status('button-b')
    mt_poll()
    sleep(20)
