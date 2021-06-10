import asyncio
from os import error
import typing as t

from . import errors
from .connection import Connection


class Server:
    def __init__(self) -> None:
        self.socket = None

    async def _handle_connection(self, r, w):
        connection = Connection(self, r, w)

        request = None
        try:
            request = await connection.parse()
        except errors.VersionError:
            # https://datatracker.ietf.org/doc/html/rfc7231#section-6.6.6
            raise
        except (errors.BadRequestError, ValueError):
            # https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.1
            raise
        except Exception:
            # https://datatracker.ietf.org/doc/html/rfc7231#section-6.6.1
            raise
        finally:
            await connection.close()

        if request is None:
            return

        print(request, request.headers)

    async def serve(self, host: str, port: int) -> t.NoReturn:
        self.socket = await asyncio.start_server(
            self._handle_connection,
            host, port
        )

        await self.socket.serve_forever()
