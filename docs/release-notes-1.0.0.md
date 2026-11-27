# Maqueen telemetry 1.0.0 - classroom pilot

Reusable telemetry that accompanies student programs in either MakeCode or MicroPython.

## Quick start

1. Download `maqueen-telemetry-v1.0.0.zip` and unzip it.
2. Flash `receiver/receiver.hex` to the spare micro:bit that stays attached to the teacher computer.
3. Run `dashboard/open_dashboard.ps1` on Windows, or use the cross-platform Python commands in the README.
4. MakeCode: add `https://github.com/henry8minus1/maqueen-telemetry` through Extensions and add the start telemetry block. Python: use `examples/starter_python.py`, or import `python/telemetry.py` alongside your program.
5. Set a unique robot ID 1-4 and the lesson tag; match it in the dashboard's Expected lesson field.

The separate HEX downloads are the same files included in the ZIP. Starter programs never drive motors. Import a starter into the corresponding editor and extend it. Include the library in your own program rather than flashing a starter over work you want to keep.

## Included and verified

- MakeCode extension, background task, and source-restorable starter HEX; compiled with official MakeCode tools.
- MicroPython module using V2 scheduled callbacks, manual fallback, single-file starter and HEX.
- Shared receiver and four-slot graphical dashboard, including measured LED pixel brightness.
- Teacher guide for micro:bit classroom distribution, unique IDs and running-version checks.
- MIT license, sources, build tools and automated tests.

Both MakeCode and MicroPython sent version, lesson identity and actual LED data through the shared receiver on two physical V2 boards. The W8 application was restored with the reusable Python module and verified reporting `w8-v1`. Host tests cover scheduling/fallback, decoding, partial LED loss, malformed frames and four-ID separation.

## Pilot limits

Four physical robots have not been tested together. Cooperative tasks can be delayed by student code. Radio packets are best effort. Extra Maqueen polling is disabled by default and can affect the built-in follower. Ultrasonic distance is supplied by the student application; telemetry does not claim its pins or initialize the board. Tags are self-reported, not authenticated program hashes. This does not install a permanent agent underneath replacement programs.

Windows USB copying can produce error 521; retry a valid HEX using an unbuffered transfer or the official editor's WebUSB flow. Verify the running tag/version after flashing.

Classroom can distribute/review editor code, but students still transfer it to their boards. No classroom session has been created automatically.
