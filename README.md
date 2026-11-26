# Maqueen telemetry

Reusable, cooperative telemetry for **Maqueen Lite V5 + micro:bit V2**, with a graphical four-robot desktop dashboard and one USB receiver. MIT licensed. Version **1.0.0**.

Telemetry is compiled/downloaded **alongside each student's program**. It is not a separate service that survives replacing the program. It never commands motors, initializes/resets the Maqueen, changes the display, or consumes button events.

## Downloads

Use the [latest release](https://github.com/henry8minus1/maqueen-telemetry/releases/latest) for the complete ZIP, receiver HEX, and starter HEX files. Or choose **Code → Download ZIP**. Four robots require five micro:bits total, including the receiver.

1. Flash `receiver.hex` to the micro:bit that stays plugged into the teacher's computer.
2. Start `dashboard/open_dashboard.ps1` on Windows (Python 3 with Tk required). On macOS/Linux: `python3 -m pip install -r dashboard/requirements.txt`, then `python3 dashboard/robot_dashboard.py`. Select the receiver's serial port.
3. Give every robot a different ID, **1–4**. Add telemetry to its program using one of the options below.
4. Check the dashboard for the intended **lesson tag, telemetry version and runtime**, as well as live LEDs and readings.

## MakeCode: add one start block

In [MakeCode](https://makecode.microbit.org/), open **Extensions** and paste:

`https://github.com/henry8minus1/maqueen-telemetry`

Add **Robot telemetry → start telemetry robot 1 lesson "lesson1-v1"** to `on start`. Continue using your normal blocks. Change the ID per robot. The extension runs a cooperative background fiber. Calling start again updates the settings without creating another fiber.

```typescript
robotTelemetry.start(1, "lesson1-v1")
basic.showIcon(IconNames.Happy)
// Your normal code, events and forever blocks go here.
```

`pollMaqueen(true)` enables extra sensor reads; leave it **off** while using the Maqueen's built-in line follower. `status("following", 70, 70)` reports application mode and commanded motor values, but never sets motors. `distance(cm)` forwards a distance your application already measured, avoiding conflicts on ultrasonic pins.

This repository is directly importable by URL. It has not been submitted for approval in the searchable MakeCode extension gallery. MakeCode Python is a different language/runtime from MicroPython; use the MakeCode blocks/TypeScript extension there.

## MicroPython: import and start

Add `python/telemetry.py` to your project files in the micro:bit Python Editor, alongside `main.py`. Use `examples/main.py` as the starting point:

```python
from microbit import *
import telemetry
print(telemetry.start(1, 'lesson1-v1'))
# Normal student program continues here.
while True:
    telemetry.poll()
    sleep(20)
```

On V2 runtimes with `microbit.run_every`, `start()` schedules callbacks and returns `background`. Older runtimes return `manual`: keep `telemetry.poll()` in your main loop. `poll()` is harmless when background scheduling is active. Long non-yielding code can delay cooperative tasks. `stop()` silences telemetry; it does not stop the robot. Repeated start calls do not duplicate scheduled callbacks.

For easy classroom sharing, `examples/starter_python.py` is a generated **single-file** starter with `mt_start`, `mt_poll`, `mt_status`, etc. The release includes its ready-to-flash HEX. It needs no separate Python module. Rebuild it with `python tools/build_starter.py` after changing the library.

## Background does not mean zero interference

Radio airtime and processor time are shared. Four robots should have unique IDs; timings are staggered but radio collisions remain possible. Use a different radio group/channel for separate classes by editing both libraries and receiver together. Student code must not reconfigure the same radio to an incompatible group, address, channel or rate. Bluetooth/radio use and I2C transactions may conflict with student programs. Avoid slow radio work in hard interrupt handlers. Extra Maqueen polling is opt-in because it affected the onboard follower during our tests.

## Measurements and freshness

Default: ID, lesson tag (13 ASCII characters), library version, runtime, buttons, acceleration, chip temperature, mode, application-reported motor commands and actual LED brightness sampled from the screen. The 25 pixels are sent in two adjacent frames; the receiver combines only a matching pair.

Optional: digital/analog line sensors, left/right light levels and the board's battery estimate. Initialize your Maqueen in your own program before enabling these reads. No sensor initialization, battery-type selection, compass calibration or ultrasonic triggers are performed by telemetry. Distance must be supplied with `distance()`. Unavailable/stale values are labeled. The reusable package does not currently sample IR, microphone, logo touch or magnetic heading automatically.

A complete cycle is about 2.3–2.5 seconds. Very brief LED animation frames can be missed. LEDs update only after both halves arrive. Packet delivery and events are best effort. The compact receiver counts forwarded packets; its count does **not** measure over-the-air loss. Raw byte sequence is exposed as `wire_seq` for diagnostics. Version and lesson labels are self-reported configuration checks, not cryptographic proof of the entire program.

## Classroom workflow

See [the teacher guide](docs/classroom.md) for starter distribution, per-robot setup and checking the running lesson tag. Classroom helps distribute/review editor code; the radio dashboard helps observe the running device.

## Repository layout

- `telemetry.ts`, `pxt.json`: MakeCode extension.
- `python/telemetry.py`: MicroPython module.
- `examples/`: separate-file and single-file Python starters; `test.ts`: MakeCode starter.
- `receiver/`: receiver source and shared decoder.
- `dashboard/`: graphical desktop app and dependency/launcher files.
- `tests/`: mocked library/decoder/fleet tests; `docs/protocol.md`: wire format.

## Verification status

See release notes and [validation details](docs/validation.md). Host tests are not substitutes for physical four-robot radio/load tests. This is an initial classroom pilot, not a safety or remote-stop system. Use the robot's own stop control.

## Sources

- [MakeCode background tasks](https://makecode.microbit.org/reference/control/in-background)
- [MicroPython V2 run_every](https://microbit-micropython.readthedocs.io/en/v2-docs/microbit.html)
- [MakeCode extension import](https://support.microbit.org/support/solutions/articles/19000054952-makecode-extension-approval)
- [DFRobot Maqueen V5](https://wiki.dfrobot.com/mbt0046/)

## Supported targets

* for PXT/microbit
