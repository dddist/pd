import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

p = GPIO.PWM(12, 150)  # channel=12 frequency=50Hz
p.start(0)
try:
    while 1:
#            p.ChangeDutyCycle(90)
#            time.sleep(2)
            p.ChangeDutyCycle(100)
            time.sleep(2)
except KeyboardInterrupt:
    pass
p.stop()
GPIO.cleanup()
