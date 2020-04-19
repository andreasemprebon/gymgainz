from asyncio import AbstractEventLoop
from measurements_handler import MeasurementsHandler
from enum import Enum
import asyncio


class Command(Enum):
    START_MEASUREMENTS = "start"
    END_MEASUREMENTS = "end"


SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 65432
CONTENT_MAX_LENGTH = 4096


class SocketHandler(object):
    def __init__(self, event_loop: AbstractEventLoop, measurements_handler: MeasurementsHandler):
        self.event_loop = event_loop
        self.event_loop.create_task(self.create_socket())

        self.measurements_handler = measurements_handler

    async def create_socket(self):
        server = await asyncio.start_server(self.handle_client, SOCKET_HOST, SOCKET_PORT)
        await server.serve_forever()

    async def handle_client(self, reader, writer):
        request = None
        try:
            while request != 'quit':
                request = (await reader.read(CONTENT_MAX_LENGTH)).decode('utf8')
                response = self.process_command(request)
                writer.write(response.encode('utf8'))
                await writer.drain()
        except ConnectionResetError:
            print("Client disconnected")
            # Client disconnected
        finally:
            writer.close()

    def process_command(self, command: str) -> str:
        if command == Command.START_MEASUREMENTS.value:
            self.measurements_handler.set_record_measurements(True)
            return "Start recording measurements"

        if command == Command.END_MEASUREMENTS.value:
            self.measurements_handler.set_record_measurements(False)
            self.measurements_handler.reset_recorded_measurements()
            return "Stop recording measurements"

        return "Unknown command"
