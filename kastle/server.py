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
import traceback
from http import HTTPStatus
from typing import Optional

from . import errors
from .utils import log
from .connection import Connection


class ServerResponse:
    def __init__(self, status: HTTPStatus, data: Optional[bytes]=None) -> None:
        self._status = status
        self._headers = {}
        self.data = data

    def add_header(self, name: str, value: str) -> None:
        self._headers[name] = value

    def to_bytes(self) -> bytes:
        lines = []

        lines.append("HTTP/1.1 {0.value} {0.phrase}".format(self._status))

        for name, value in self._headers.items():
            lines.append(f"{name}:{value}")

        lines.append('')

        data = self.data
        if not data:
            data = ''
        else:
            self.add_header("Content-Length", len(data))

        lines.append(data)

        lines = [line.encode('ascii') for line in lines]

        return b"\r\n".join(lines)


class Server:
    __slots__ = ('host', 'port', 'socket')

    def __init__(self):
        # To be filled later.
        self.host = None
        self.port = None
        self.socket = None

    def can_handle(self, verb, target) -> bool:
        return True

    async def http_error(self, status: HTTPStatus, error, connection):
        response = ServerResponse(status)
        response.data = str(error)

        response = response.to_bytes()

        try:
            await connection.send(response)
        except Exception:
            traceback.print_exc()

        await connection.close()

    async def serve(self, host: str, port: int):
        self.host = host
        self.port = port

        self.socket = await asyncio.start_server(
            self._handle_raw_connection,
            host, port
        )

        log('info', f'Server started at http://{host}:{port}')

        await self.socket.serve_forever()

    async def _handle_raw_connection(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        connection = Connection(self, reader, writer)

        request = None
        try:
            request = await connection.parse()
        except errors.HTTPVersionNotSupported as e:
            return await self.http_error(HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,e, connection)
        except errors.BadRequest as e:
            return await self.http_error(HTTPStatus.BAD_REQUEST, e, connection)
        except errors.NotFound as e:
            return await self.http_error(HTTPStatus.NOT_FOUND, e, connection)
        except Exception as e:
            return await self.http_error(HTTPStatus.INTERNAL_SERVER_ERROR, e, connection)

        if request is None:
            return await connection.close()

        try:
            await self._handle_connection(request, connection)
        except Exception as e:
            return await self.http_error(HTTPStatus.INTERNAL_SERVER_ERROR, e, connection)

        await connection.close()

    async def _handle_connection(self, request, connection) -> None:
        response = ServerResponse(HTTPStatus.OK, "OK")
        response = response.to_bytes()

        await connection.send(response)
