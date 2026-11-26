"""Maqueen telemetry 1.0.0. V2 run_every scheduler, or explicit poll() fallback.
Never resets the board, changes LEDs, reads button events, or commands motors.
"""
import microbit as mb
import radio

VERSION = '1.0.0'
_robot = 1
_tag = 'starter'
_seq = 0
_phase = -1
_enabled = False
_scheduled = False
_period = 200
_last = 0
_sensors = False
_mode = 'idle'
_commands = (0, 0)
_cm = -1
_errors = 0

def _clean(value):
    return ''.join(c for c in str(value) if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.')[:13] or 'starter'

def _send(kind, value):
    global _seq
    _seq = (_seq + 1) & 255
    payload = str(value)
    if len(payload) > 13:
        return
    radio.send_bytes(('MT%d%s%02x%s' % (_robot, kind, _seq, payload)).encode('ascii'))

def _read(reg, count=1):
    mb.i2c.write(16, bytes([reg]))
    return int.from_bytes(mb.i2c.read(16, count), 'big')

def _tick():
    global _phase, _errors
    if not _enabled:
        return
    _phase = (_phase + 1) % 12
    try:
        if _phase == 0:
            _send('H', VERSION + '|python')
        elif _phase == 1:
            _send('N', _tag)
        elif _phase == 2:
            _send('B', '%d%d' % (mb.button_a.is_pressed(), mb.button_b.is_pressed()))
        elif _phase in (3, 4):
            start, end = (0, 13) if _phase == 3 else (13, 25)
            _send('U' if _phase == 3 else 'V', ''.join(str(mb.display.get_pixel(i % 5, i // 5)) for i in range(start, end)))
        elif _phase == 5:
            _send('A', '%d,%d' % (mb.accelerometer.get_x(), mb.accelerometer.get_y()))
        elif _phase == 6:
            _send('Z', mb.accelerometer.get_z())
        elif _phase == 7:
            _send('T', mb.temperature())
        elif _phase == 8:
            _send('M', _mode)
        elif _phase == 9:
            _send('C', '%d,%d' % _commands)
        elif _phase == 10:
            _send('D', _cm)
        elif _phase == 11:
            _send('Q', int(_sensors))
        if _sensors:
            if _phase == 0:
                _send('L', _read(29) & 7)
            elif _phase == 1:
                _send('E', '%d,%d' % (_read(32, 2), _read(34, 2)))
            elif _phase == 2:
                _send('F', _read(36, 2))
            elif _phase == 6:
                _send('I', '%d,%d' % (_read(41, 2), _read(43, 2)))
            elif _phase == 7:
                _send('K', _read(46))
    except Exception:
        _errors += 1

def start(robot_id=1, program_tag='starter', background=True):
    """Returns background/manual. Repeated calls do not duplicate scheduled tasks."""
    global _robot, _tag, _enabled, _scheduled, _period
    if robot_id not in (1, 2, 3, 4):
        raise ValueError('robot_id must be 1-4')
    _robot, _tag = robot_id, _clean(program_tag)
    radio.config(group=83, channel=17, address=0x75626974, length=32, queue=4, power=6)
    radio.on()
    _period = 180 + robot_id * 7
    _enabled = True
    scheduler = getattr(mb, 'run_every', None)
    if background and scheduler is not None and not _scheduled:
        scheduler(_tick, ms=_period)
        _scheduled = True
    return 'background' if _scheduled else 'manual'

def poll():
    """Call each iteration if start() returns manual; harmless when scheduled."""
    global _last
    now = mb.running_time()
    if not _scheduled and now - _last >= _period:
        _last = now
        _tick()

def poll_maqueen(enabled=True):
    global _sensors
    _sensors = bool(enabled)

def status(mode='idle', left=0, right=0):
    """Application-reported commands, not wheel feedback. Never drives motors."""
    global _mode, _commands
    _mode = _clean(mode)
    _commands = (max(-255, min(255, int(left))), max(-255, min(255, int(right))))

def distance(cm):
    global _cm
    _cm = int(cm) if cm is not None else -1

def stop():
    global _enabled
    _enabled = False

def errors():
    return _errors

