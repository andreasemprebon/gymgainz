from sensor_readings import SensorReadings
from measurements_handler import MeasurementsHandler
from socket_handler import SocketHandler
import asyncio

loop = asyncio.get_event_loop()

sensor_reading = SensorReadings(event_loop=loop)
measurements_handler = MeasurementsHandler(measurements_subject=sensor_reading.measurements_subject)
socket_handler = SocketHandler(event_loop=loop, measurements_handler=measurements_handler)

sensor_reading.start()

loop.run_forever()
