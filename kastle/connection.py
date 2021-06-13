import asyncio
from typing import Dict

from . import errors

CRLN = b"\r\n"


class Request:
    __slots__ = ("verb", "target", "version", "_headers", "_body")

    def __init__(self, method: bytes, target: bytes, version: bytes) -> None:
        self.method = method
        self.target = target
        self.version = version

        self._headers = {}
        self._body = b''

    @property
    def headers(self) -> Dict[bytes, bytes]:
        if type(self._headers) is not dict:
            temp = {}

            for header in self._headers:
                name, value = header.split(b':', 1)
                temp[name] = value

            self._headers = temp

        return self._headers

    @property
    def body(self) -> bytes:
        return self._body


class Connection:
    __slots__ = ("server", "reader", "writer")

    def __init__(self,
                 server,
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter) -> None:

        self.server = server
        self.reader = reader
        self.writer = writer

    async def close(self) -> None:
        self.writer.close()

    def send(self, data: bytes) -> None:
        self.writer.write(data)
        return self.writer.drain()

    async def parse(self) -> None:
        firstline = await self.reader.readline()

        try:
            method, target, version = firstline.split(b' ')
        except ValueError:
            raise errors.BadRequest(firstline)

        version = version.strip(CRLN)

        if version != b"HTTP/1.1":
            raise errors.HTTPVersionNotSupported(version)

        if not self.server.can_handle(method, target):
            raise errors.NotFound(method, target)

        request = Request(method, target, version)

        headers = []
        async for line in self.reader:
            if line == CRLN:
                break

            headers.append(line)

        if headers:
            request._headers = headers

            clen = request.headers.get(b"Content-Length", 0)
            request._body = await self.reader.readexactly(clen)

        return request
