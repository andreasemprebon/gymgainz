from rx.subject import Subject
from rx import operators as ops
from measure import Measure


class MeasurementsHandler(object):
    def __init__(self, measurements_subject: Subject):
        self.record_measurements = True
        self.recorded_values = []

        measurements_subject.pipe(
            ops.filter(lambda measure: self.record_measurements)
        ).subscribe_(on_next=self.received_measure)

    def set_record_measurements(self, should_record_measurements: bool):
        self.record_measurements = should_record_measurements

    def reset_recorded_measurements(self):
        self.recorded_values = []

    def received_measure(self, measure: Measure):
        self.recorded_values.append(measure)
        print("{},{},{},{}".format(measure.timestamp,
                                   measure.angular_speed_in_radians_per_second,
                                   measure.direction,
                                   measure.tangential_speed_in_meters_per_second))
