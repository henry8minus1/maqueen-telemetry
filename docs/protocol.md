# Compact protocol 1

Radio: group 83, channel 17, address `0x75626974`, 1 Mbit/s, 32-byte packet configuration. MicroPython sends ASCII bytes directly. MakeCode uses its official `radio.sendString` envelope: byte 0 type 2, bytes 1–4 system time, 5–8 serial, byte 9 payload length, then string. Decoder accepts an optional `01 00 01` datagram prefix. No substring scanning is used.

Text frame: `MT` + one-digit robot ID + one-character kind + two hexadecimal sequence digits + up to 13 ASCII payload characters. Total <=19 characters. The byte sequence increments modulo 256 per transmitted frame.

| Kind | Payload |
| --- | --- |
| H | `1.0.0|python` or `1.0.0|pxt` |
| N | Lesson/build tag, <=13 safe ASCII characters |
| B | Two button bits, A then B |
| U / V | First 13 / last 12 LED brightness digits, row-major 0–9 |
| A / Z | Acceleration x,y / z, mg |
| T | Chip temperature, C |
| M | Application mode |
| C | Application-supplied motor commands left,right |
| D | Application-supplied cm; -1 unavailable |
| Q | Optional Maqueen polling enabled 0/1 |
| L | Line black mask left=4, center=2, right=1 |
| E / F | Analog line L,C / R |
| I | Ambient light L,R |
| K | Board battery percentage estimate |

Receiver forwards `R <RSSI> <JSON>` to USB at 115200 baud. JSON is `[2,robotId,forwardedCount,receiverMs,"state",data]`, compatible with the fleet dashboard. It includes `wire_seq`. The time is receiver uptime, not sender uptime. Forwarded count is not an RF loss counter. Malformed or unknown frames are ignored. An LED pair needs adjacent wire sequence numbers and receipt within 2 seconds, preventing mixed snapshots after a missing half.

Wire labels are self-reported, unauthenticated and visible to nearby radios. Telemetry does not receive commands or control motors. This compact protocol replaces the earlier project-specific JSON transmitter and needs the package receiver firmware; keep all components at the same release.

