import asyncio
import socket
import sys


class Protocol(asyncio.DatagramProtocol):
    @staticmethod
    def connection_made(transport):
        print("connect")

    @staticmethod
    def datagram_received(data, addr):
        print("received", data, "from", addr)


async def connect():
    loop = asyncio.get_event_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: Protocol,
        local_addr=('0.0.0.0', 9000))
    await asyncio.sleep(5.0)
    return transport


async def send(addrs):
    transport = await connect()
    for a in addrs:
        print('sending to', a)
        transport.sendto(b'hi', (a, 9000))


if __name__ == '__main__':
    mode = sys.argv[1]
    assert mode in ('send', 'receive')
    loop = asyncio.get_event_loop()
    if mode == 'send':
        others = sys.argv[2:]
        addrs = [socket.gethostbyname(h) for h in others]
        loop.run_until_complete(send(addrs))
    else:
        loop.run_until_complete(connect())
    loop.run_until_complete(asyncio.sleep(5.0))
