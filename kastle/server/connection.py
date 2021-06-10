import asyncio

from . import errors
from .request import Request


class Connection:
    def __init__(self,
                 s,
                 r: asyncio.StreamReader,
                 w: asyncio.StreamWriter) -> None:

        self.server = s
        self.reader = r
        self.writer = w

    async def close(self):
        self.writer.close()

    async def parse(self):
        first_line = await self.reader.readline()
        if not first_line:
            return

        verb, path, version = first_line.split()
        if version != b"HTTP/1.1":
            raise errors.VersionError(version)

        headers = bytearray()
        async for line in self.reader:
            if line == b'\r\n':
                break

            headers.extend(line)

        request = Request(verb, path, version, headers)

        length = request.headers.get("Content-Length")
        if length is not None:
            if not length.isdigit():
                raise errors.BadRequestError()

            length = int(length)
            request._body = await self.reader.readexactly(length)

        return request
