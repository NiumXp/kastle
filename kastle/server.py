'''
MIT License

Copyright (c) 2021 Caio Alexandre

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import asyncio

from .utils import log


_RECV_BYTES = 1024


class Server:
    __slots__ = ('host', 'port', 'socket')

    def __init__(self):
        # To be filled later.
        self.host = None
        self.port = None
        self.socket = None

    async def serve(self, host: str, port: int):
        self.host = host
        self.port = port

        self.socket = await asyncio.start_server(
            self.connection_callback,
            host, port
        )

        log('info', f'Server started at http://{host}:{port}')

        await self.socket.serve_forever()

    async def connection_callback(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ):
        received_data = await reader.read(n=_RECV_BYTES)

        writer.write(b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK')
        await writer.drain()

        writer.close()
