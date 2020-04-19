from asyncio import AbstractEventLoop
from measurements_handler import MeasurementsHandler
from enum import Enum
import websockets


class Command(Enum):
    START_MEASUREMENTS = "start"
    END_MEASUREMENTS = "end"


SOCKET_PORT = 65432


class SocketHandler(object):
    def __init__(self, event_loop: AbstractEventLoop, measurements_handler: MeasurementsHandler):
        self.event_loop = event_loop
        self.event_loop.create_task(self.create_socket())

        self.measurements_handler = measurements_handler

    async def create_socket(self):
        await websockets.serve(self.handle_client, port=SOCKET_PORT)

    async def handle_client(self, web_socket, path):
        request = await web_socket.recv()
        response = self.process_command(request)
        await web_socket.send(response)

    def process_command(self, command: str) -> str:
        if command == Command.START_MEASUREMENTS.value:
            self.measurements_handler.set_record_measurements(True)
            return "Start recording measurements"

        if command == Command.END_MEASUREMENTS.value:
            self.measurements_handler.set_record_measurements(False)
            self.measurements_handler.reset_recorded_measurements()
            return "Stop recording measurements"

        return "Unknown command"
