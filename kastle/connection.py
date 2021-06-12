import asyncio
from typing import Optional, Dict
from functools import cached_property

from . import errors

CRLN = b"\r\n"


class Request:
    __slots__ = ("verb", "target", "version", "_headers", "_body")

    def __init__(self, verb: bytes, target: bytes, version: bytes) -> None:
        self.verb = verb
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
                 s,
                 r: asyncio.StreamReader,
                 w: asyncio.StreamWriter) -> None:

        self.server = s
        self.reader = r
        self.writer = w

    async def close(self) -> None:
        self.writer.close()

    def send(self, data: bytes) -> None:
        self.writer.write(data)
        return self.writer.drain()

    async def parse(self) -> None:
        firstline = await self.reader.readline()

        try:
            verb, target, version = firstline.split(b' ')
        except ValueError:
            raise errors.BadRequest(firstline)

        version = version.strip(CRLN)

        if version != b"HTTP/1.1":
            raise errors.HTTPVersionNotSupported(version)

        if not self.server.can_handle(verb, target):
            raise errors.NotFound(verb, target)

        request = Request(verb, target, version)

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
