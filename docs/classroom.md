# Teacher workflow: classroom + live device confirmation

micro:bit classroom distributes and reviews programs in student editors. It does not install a permanent telemetry layer or prove the code currently executing on a board. Use it alongside the dashboard.

## Prepare before class

1. Label robots 1–4. Keep the receiver separate and attached to your computer.
2. Flash the package's receiver HEX; open the dashboard and choose its serial port.
3. Choose a short lesson identifier, e.g. `line1-v1`. Set the same expected lesson field in the dashboard.
4. Prepare a MakeCode starter containing the telemetry extension and one start block, or the single-file `examples/starter_python.py`. For MakeCode, download the starter HEX to retain its extension references.
5. Test the starter on one actual robot. Confirm live pixels, ID, runtime, tag and library version before distributing it.

## Run a session

1. Open [micro:bit classroom](https://classroom.microbit.org/) and create an activity. Choose **MakeCode** or **Python (MicroPython)**. The official classroom guide says MakeCode Python is not supported.
2. In the teacher editor, import the starter HEX or load the starter Python code. Choose **Share code with students**.
3. Students join via [microbit.org/join](https://microbit.org/join), using the session words and PIN. Have each student set their assigned robot ID. Distribute distinct starters individually if needed.
4. Students accept the shared code and transfer it to their physical boards using Download / Send to micro:bit. Sharing editor code alone does not flash a board. Each student must connect and authorize their local board's transfer.
5. Check the dashboard: the assigned slot should be live, with the intended lesson tag and library version. Press a physical robot button or change its LED picture and confirm the matching panel responds.
6. Review student code in Classroom's **Student code** view. If a robot reports the wrong tag, check its start call and flash the correct program again. A missing radio report is ambiguous: power, radio settings, wrong program, or missing telemetry can all cause it.

Sharing new teacher code replaces the student's editor contents after acceptance; save student work before replacing it. Do not overwrite their programs merely to change telemetry; include the extension/module in the starter and let their work continue below it.

## Save and resume

Download the classroom HTML session file through **Save classroom**. The official guide says students' work is not stored online between sessions. Restoring the saved file creates new joining details. Keep release ZIPs/starter HEX files with the lesson materials so the library version is reproducible.

## Limits

The dashboard confirms a fresh, self-reported tag/version, not an unmodified program hash. Four physical robots have not yet been tested simultaneously. Unique IDs are required; duplicate IDs mix readings. Do not publish student names or logs to the public repository. No classroom session or student invitations are created by installing this package.

Sources: [Official classroom guide](https://support.microbit.org/support/solutions/articles/19000108079-guide-to-using-micro-bit-classroom), [Classroom FAQ](https://support.microbit.org/support/solutions/articles/19000107544-micro-bit-classroom-faq), [Transfer programs](https://www.microbit.org/get-started/user-guide/transfer-code-to-the-microbit/).
