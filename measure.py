import time


class Measure(object):
    def __init__(self,
                 angular_speed_in_radians_per_second: float,
                 tangential_speed_in_meters_per_second: float,
                 direction: int):
        self.timestamp = time.time()
        self.angular_speed_in_radians_per_second = angular_speed_in_radians_per_second
        self.tangential_speed_in_meters_per_second = tangential_speed_in_meters_per_second
        self.direction = direction
