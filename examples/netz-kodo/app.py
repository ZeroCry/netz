import asyncio
import hashlib
import os
import socket
import sys

import kodo

SYMBOLS = 8
SYMBOL_SIZE = 160


class Sender(asyncio.DatagramProtocol):
    @staticmethod
    def connection_made(transport):
        print("connect")

    @staticmethod
    def datagram_received(data, addr):
        print("received", data, "from", addr)


class Receiver(asyncio.DatagramProtocol):
    def __init__(self):
        decoder_factory = kodo.FullVectorDecoderFactoryBinary(
            SYMBOLS, SYMBOL_SIZE)
        self.decoder = decoder_factory.build()
        self.received = 0
        self.data = asyncio.Future()

    def connection_made(self, transport):
        print("connect")

    def datagram_received(self, data, addr):
        self.decoder.read_payload(data)
        self.received += len(data)
        if self.decoder.is_complete() and not self.data.done():
            self.data.set_result(self.decoder.copy_from_symbols())


async def send(addrs):
    transport, _ = await asyncio.get_event_loop().create_datagram_endpoint(
        lambda: Sender,
        local_addr=('0.0.0.0', 9000))
    encoder_factory = kodo.FullVectorEncoderFactoryBinary(SYMBOLS, SYMBOL_SIZE)
    encoder = encoder_factory.build()
    data = os.urandom(encoder.block_size())
    await asyncio.sleep(5.0)
    print('Sending {} B of random data with hash {}'.format(
        len(data), hashlib.sha256(data).hexdigest()))

    encoder.set_const_symbols(data)

    while True:
        packet = encoder.write_payload()
        transport.sendto(packet, (destination, 9000))


async def receive():
    trans, proto = await asyncio.get_event_loop().create_datagram_endpoint(
        lambda: Receiver(),
        local_addr=('0.0.0.0', 9000))

    data = await proto.data
    trans.close()
    print('Received data with hash {}'.format(
        hashlib.sha256(data).hexdigest()))


if __name__ == '__main__':
    mode = sys.argv[1]
    assert mode in ('send', 'receive')
    loop = asyncio.get_event_loop()
    if mode == 'send':
        destination = socket.gethostbyname(sys.argv[2])
        loop.run_until_complete(send(destination))
    else:
        loop.run_until_complete(receive())
