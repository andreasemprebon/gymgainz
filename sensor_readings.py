import asyncio
from asyncio import AbstractEventLoop
import RPi.GPIO as GPIO
import threading
import math
import time
from rx.subject import Subject
from measure import Measure

# Useful links
# Encoder datasheet: https://www.robotshop.com/uk/incremental-photoelectric-rotary-encoder-400p-r.html
# Wiring: https://pinout.xyz/pinout/wiringpi
# Encoder speed measurement: https://www.motioncontroltips.com/how-are-encoders-used-for-speed-measurement/
# PiScope: http://abyz.me.uk/rpi/pigpio/piscope.html

# GPIO Ports
# Encoder input A: input GPIO 27
# Encoder input B: input GPIO 22
ENCODER_PIN_A = 27
ENCODER_PIN_B = 22

# Encoder parameters
PULSES_PER_ROTATION = 400

# It is the radius in meters of the wheel where the wire is attached
WHEEL_RADIUS_IN_METERS = 0.03


class SensorReadings(object):
    def __init__(self, event_loop: AbstractEventLoop):
        self.event_loop = event_loop

        # It contains the pulses recorded for each time interval
        self.pulse_count = 0

        # It is incremented by 1 for every step in the up direction
        # and decremented by 1 for every step in the down direction
        # After each time interval, its sign is evaluated and it will
        # be +1 for up movements and -1 for down movements
        self.direction_count = 0

        self.last_state_a = 1
        self.last_state_b = 1

        self.rotatory_lock = threading.Lock()

        self.measurements_subject = Subject()

        self.gpio_init()

    # Initialize interrupt handlers
    def gpio_init(self):
        GPIO.setwarnings(True)

        # Use BCM mode
        GPIO.setmode(GPIO.BCM)

        # define the Encoder switch inputs
        GPIO.setup(ENCODER_PIN_A, GPIO.IN)
        GPIO.setup(ENCODER_PIN_B, GPIO.IN)

        # setup callback thread for the A and B encoder
        # use interrupts for all inputs
        GPIO.add_event_detect(ENCODER_PIN_A, GPIO.RISING, callback=self.rotary_interrupt)
        GPIO.add_event_detect(ENCODER_PIN_B, GPIO.RISING, callback=self.rotary_interrupt)
        return

    # Rotatory encoder interrupt called by both channels
    def rotary_interrupt(self, encoder_pin):
        # Read both channels
        current_state_a = GPIO.input(ENCODER_PIN_A)
        current_state_b = GPIO.input(ENCODER_PIN_B)

        # now check if state of A or B has changed
        # if not that means that bouncing caused it
        if current_state_a == self.last_state_a and current_state_b == self.last_state_b:
            return

        self.last_state_a = current_state_a
        self.last_state_b = current_state_b

        # We want to count only when both channels are up because
        # it means it's the start of a new rotation
        if current_state_b == 0 or self.last_state_a == 0:
            return

        # Turning direction depends on which channel is up first
        # If the channel ENCODER_PIN_A is up first, it's a movement
        # going up. If it's ENCODER_PIN_B the first channel, it's a
        # down movement
        if encoder_pin == ENCODER_PIN_B:
            direction_increment = -1  # Down movement
        else:
            direction_increment = 1  # Up movement

        self.rotatory_lock.acquire()
        self.pulse_count += 1
        self.direction_count += direction_increment
        self.rotatory_lock.release()  # and release lock

        return

    def start(self):
        self.event_loop.create_task(self.start_thread())

    async def start_thread(self):
        while True:
            start_time = time.monotonic()
            await asyncio.sleep(0.01)
            elapsed_time = time.monotonic() - start_time

            # Get the current pulses
            self.rotatory_lock.acquire()
            pulses_during_the_interval = self.pulse_count
            direction_during_the_interval = int(math.copysign(1, self.direction_count))

            # Reset Values
            self.pulse_count = 0
            self.direction_count = 0
            self.rotatory_lock.release()

            if pulses_during_the_interval != 0:
                angular_speed_in_radians_per_second = (2 * math.pi * pulses_during_the_interval) / \
                                                      (PULSES_PER_ROTATION * elapsed_time)
                # angular_speed_in_degree_per_second = angular_speed_in_radians_per_second * 180 / math.pi
                tangential_speed_in_meters_per_second = angular_speed_in_radians_per_second * WHEEL_RADIUS_IN_METERS

                measure = Measure(angular_speed_in_radians_per_second,
                                  tangential_speed_in_meters_per_second,
                                  direction_during_the_interval)
                self.measurements_subject.on_next(measure)

        self.measurements_subject.dispose()
