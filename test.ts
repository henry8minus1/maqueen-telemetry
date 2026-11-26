robotTelemetry.start(1, "lesson1-v1")
basic.showIcon(IconNames.Happy)
input.onButtonPressed(Button.A, function () {
    robotTelemetry.status("button-a", 0, 0)
    basic.showString("A")
})

