/** Cooperative, read-only telemetry; never initializes or drives the Maqueen. */
//% color=#087f8c icon="\uf1eb" block="Robot telemetry"
namespace robotTelemetry {
    let enabled = false
    let started = false
    let robot = 1
    let sequence = 0
    let phase = 0
    let period = 180
    let lesson = "starter"
    let sensorReads = false
    let cm = -1
    let leftCommand = 0
    let rightCommand = 0
    let mode = "idle"
    function send(kind: string, payload: string) {
        sequence = (sequence + 1) & 255
        const hex = "0123456789abcdef"
        radio.sendString("MT" + robot + kind + hex.charAt(sequence >> 4) + hex.charAt(sequence & 15) + payload.substr(0, 13))
    }
    function word(reg: number): number {
        pins.i2cWriteNumber(16, reg, NumberFormat.UInt8BE)
        return pins.i2cReadNumber(16, NumberFormat.UInt16BE)
    }
    function byte(reg: number): number {
        pins.i2cWriteNumber(16, reg, NumberFormat.UInt8BE)
        return pins.i2cReadNumber(16, NumberFormat.UInt8BE)
    }
    function clean(value: string): string {
        let out = ""
        for (let i = 0; i < value.length && out.length < 13; i++) {
            let ch = value.charCodeAt(i)
            if ((ch >= 48 && ch <= 57) || (ch >= 65 && ch <= 90) || (ch >= 97 && ch <= 122) || ch == 45 || ch == 95 || ch == 46) out += value.charAt(i)
        }
        return out || "starter"
    }
    function tick() {
        phase = (phase + 1) % 12
        if (phase == 0) send("H", "1.0.0|pxt")
        else if (phase == 1) send("N", lesson)
        else if (phase == 2) send("B", (input.buttonIsPressed(Button.A) ? "1" : "0") + (input.buttonIsPressed(Button.B) ? "1" : "0"))
        else if (phase == 3 || phase == 4) {
            let pixels = ""
            // Three rows, then two rows; 13-byte payload requires 13/12 split.
            for (let i = phase == 3 ? 0 : 13; i < (phase == 3 ? 13 : 25); i++) {
                pixels += Math.round(led.pointBrightness(i % 5, Math.idiv(i, 5)) * 9 / 255)
            }
            send(phase == 3 ? "U" : "V", pixels)
        } else if (phase == 5) send("A", input.acceleration(Dimension.X) + "," + input.acceleration(Dimension.Y))
        else if (phase == 6) send("Z", "" + input.acceleration(Dimension.Z))
        else if (phase == 7) send("T", "" + input.temperature())
        else if (phase == 8) send("M", mode)
        else if (phase == 9) send("C", leftCommand + "," + rightCommand)
        else if (phase == 10) send("D", "" + cm)
        else if (phase == 11) send("Q", sensorReads ? "1" : "0")
        if (sensorReads) {
            if (phase == 0) send("L", "" + (byte(29) & 7))
            else if (phase == 1) send("E", word(32) + "," + word(34))
            else if (phase == 2) send("F", "" + word(36))
            else if (phase == 6) send("I", word(41) + "," + word(43))
            else if (phase == 7) send("K", "" + byte(46))
        }
    }
    /** Start once, then run normal student code. IDs must be unique, 1-4. */
    //% block="start telemetry robot %id lesson %programTag"
    //% id.min=1 id.max=4 programTag.defl="starter"
    export function start(id: number, programTag: string) {
        robot = Math.max(1, Math.min(4, Math.round(id)))
        lesson = clean(programTag)
        radio.setGroup(83)
        radio.setFrequencyBand(17)
        radio.setTransmitPower(6)
        enabled = true
        if (!started) {
            started = true
            control.inBackground(function () {
                basic.pause(robot * 47)
                while (true) {
                    if (enabled) tick()
                    basic.pause(period + robot * 7)
                }
            })
        }
    }
    /** Extra I2C reads may affect the built-in follower; off by default. */
    //% block="telemetry Maqueen sensor polling %on"
    export function pollMaqueen(on: boolean) { sensorReads = on }
    /** Set status from the application; this never commands the motors. */
    //% block="telemetry mode %name motor commands %left %right"
    export function status(name: string, left: number, right: number) {
        mode = clean(name); leftCommand = Math.constrain(left, -255, 255); rightCommand = Math.constrain(right, -255, 255)
    }
    /** Reuse distance already read by student code, avoiding pin ownership conflicts. */
    //% block="telemetry distance cm %distance"
    export function distance(distance: number) { cm = Math.round(distance) }
    //% block="stop telemetry"
    export function stop() { enabled = false }
}

