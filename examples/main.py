from microbit import *
import telemetry

# Change these for each robot and lesson. Choose a short ASCII lesson label.
scheduling = telemetry.start(robot_id=1, program_tag='lesson1-v1')
display.show(Image.HAPPY)

# Keep Maqueen polling OFF during its built-in line follower.
# Enable it only after testing the effect on your application:
# telemetry.poll_maqueen(True)
while True:
    if button_a.was_pressed():
        display.show('A')
        telemetry.status('button-a')
    if button_b.was_pressed():
        display.show('B')
        telemetry.status('button-b')
    telemetry.poll()  # Fallback for older runtimes; no-op when scheduled.
    sleep(20)
