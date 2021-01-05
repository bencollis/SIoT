from gpiozero import Servo
from time import sleep

servo = Servo(19)
servo.value = 0
sleep(5)

while True:
    servo.value = 0.9
    sleep(2)
    servo.value = 0
    sleep(2)
    servo.value = -0.8
    sleep(2)
    servo.value = 0
    sleep(2)
    