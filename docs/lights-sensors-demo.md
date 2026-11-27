# Lights and sensors demo

Flash `examples/lights_sensors.hex` to the robot micro:bit and the updated
`receiver/receiver.hex` to the USB receiver. Run the updated dashboard with
`python dashboard/robot_dashboard.py --port COM5 --lesson sensors-v1`.
Robot ID is 1; motors remain stopped. Press A to pause/resume lights or B
to advance. Lights change every 3.2 seconds so the matrix can be sampled.

Cover each of the two light sensors, move black/white paper under each of
the three line sensors, put a hand 10–40 cm ahead, tilt the robot, press A/B,
touch the gold logo, and clap. Sensor details lists every received field.
Point an IR remote at the receiver: `ir_activity` counts sampled low transitions,
not decoded keys, and can miss pulses. No remote test is implied by a zero count.

Magnetic field is in µT; heading is unavailable if the compass has not already
been calibrated. This demo never interrupts operation to run compass calibration.
The micro:bit ambient light reading shares its LED matrix and is affected by it.
Temperature is chip temperature; battery is the board's existing estimate/type.

Colored dashboard dots report commanded colors (two headlights then four RGB
pixels), not optical feedback. Matrix pixels are sampled. 0=off, 1=red, 2=green,
3=yellow, 4=blue, 5=purple, 6=cyan, 7=white. RGB pixels use brightness 32/255.
Power/status LEDs and line-sensor emitters are hardware controlled.
The buzzer and expansion connectors are outside this lights/sensors demo.

Protocol addition: `X` payloads contain one subtype followed by a value:
`o` six color digits, `s` sound 0–255, `t` logo 0/1, `i` IR activity count,
`h` heading degrees (-1 unavailable), `m` magnetic µT, `l` matrix light 0–255.
Old packets and library version 1.0.0 remain compatible. Use the updated receiver
to decode X frames. All radio reports are best effort; inspect ages in details.

Hardware reference: https://github.com/DFRobot/pxt-maqueen/blob/master/maqueen.ts
