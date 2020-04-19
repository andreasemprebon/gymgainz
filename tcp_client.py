import asyncio


async def tcp_echo_client(message, loop):
    reader, writer = await asyncio.open_connection('127.0.0.1',
                                                   65432,
                                                   loop=loop)

    print('Send: %r' % message)
    writer.write(message.encode('utf8'))

    data = await reader.read(4096)
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()


message_to_send = 'start'
event_loop = asyncio.get_event_loop()
event_loop.run_until_complete(tcp_echo_client(message_to_send, event_loop))
event_loop.close()
