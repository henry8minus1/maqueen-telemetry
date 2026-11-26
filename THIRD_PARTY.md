# Third-party components

Source code in this repository is MIT licensed. Compiled HEX files include the micro:bit runtime and its dependencies, under their respective licenses:

- MicroPython: [MIT license](https://github.com/micropython/micropython/blob/master/LICENSE).
- micro:bit MicroPython V2/runtime sources and notices: [microbit-foundation/micropython-microbit-v2](https://github.com/microbit-foundation/micropython-microbit-v2).
- The supplied Python runtime HEX is taken from [the official Python Editor V3](https://github.com/microbit-foundation/python-editor-v3/tree/main/src/micropython/main), not a firmware update for the USB interface.
- MakeCode: [PXT micro:bit](https://github.com/microsoft/pxt-microbit), [PXT core](https://github.com/microsoft/pxt), [PXT common packages](https://github.com/microsoft/pxt-common-packages), MIT; see repositories for runtime/dependency notices.
- Maqueen register definitions are based on [DFRobot/pxt-maqueen](https://github.com/DFRobot/pxt-maqueen), MIT.
- HEX build tooling: [microbit-fs](https://github.com/microbit-foundation/microbit-fs), MIT. Not needed to run the dashboard.
- Dashboard dependency: [pyserial](https://github.com/pyserial/pyserial), BSD 3-Clause, installed separately. Tk is part of the user's Python installation.

The repository does not bundle student names, private logs, access tokens, or local Python environments.
