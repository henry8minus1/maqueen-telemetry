# Validation

Initial 1.0.0 classroom pilot.

## Automated checks

- Python module tests: background scheduler registration and duplicate-start prevention, stop/resume semantics, explicit older-runtime polling, opt-in I2C reads, callback error recovery, frame size, metadata and LED reconstruction.
- Shared decoder tests: actual documented MakeCode envelope, native Python frames, optional datagram prefix, invalid IDs/data, missing LED fragment and sequence wrap, four isolated sender states.
- MakeCode extension + starter compiled to universal HEX using official `pxt-microbit 9.1.2` / `pxt-core 13.2.17`.
- Fleet routing/rendering previously tested for four IDs on host. No claim of four physical transmitters tested together.

Run `python -m unittest discover -s tests -v`.

## Hardware checks

- MicroPython V2 starter ran on a physical micro:bit: `microbit.run_every` was available and scheduled callbacks stayed active while the main loop handled buttons/display. Receiver forwarded runtime `python`, library `1.0.0`, lesson `lesson1-v1`, acceleration, temperature, buttons and reconstructed LEDs.
- MakeCode diagnostic background callback ran repeatedly on the same board. Raw MakeCode radio bytes were received when the MicroPython receiver used `length=32`, at 1 Mbit/s, group 83/channel 17. The official type/length/string envelope matched the decoder. Final receiver explicitly uses 32-byte packets.
- Final shared receiver and MakeCode starter verified end to end on two physical V2 boards: received `runtime=makecode`, `library_version=1.0.0`, `program_tag=lesson1-v1`, buttons, acceleration, temperature and reconstructed 25-pixel LED image.
- W8 application restored with reusable Python telemetry: received `runtime=python`, `library_version=1.0.0`, `program_tag=w8-v1`, line/analog/light readings and actual LED pixels while the robot remained idle.
- Windows produced flash error 521 during development; all source HEX checksums were valid. An unbuffered `robocopy /J` transfer recovered the receiver. Check the running tag/version after flashing.
- Packaged graphical dashboard visually verified with Robot 1 live, `MATCH w8-v1 / 1.0.0 python`, sensor readings and actual LED pixels. The other three slots remained waiting; no simulated data was displayed as live.

## Known boundaries

Cooperative background tasks can be delayed by long blocking/non-yielding student code. Telemetry shares processor/radio resources; optional I2C reads can affect line-following. Radio packets may be lost or collide. Runtime and lesson tags are self-reported, not program hashes. The receiver's forwarded counter measures USB output continuity, not RF packet loss. LED frames are snapshots, not lossless animation recordings.

MicroPython V1 and physical four-robot contention are not validated. Package targets micro:bit V2. The receiver must use this release's firmware; earlier project-specific radio addresses are incompatible.
