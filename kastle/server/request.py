from typing import Dict, Optional


class Request:
    __slots__ = ("_verb", "_path", "_version", "_headers", "_body")

    def __init__(self,
                 verb: bytearray,
                 path: bytearray,
                 version: bytearray,
                 headers: bytearray,
                 body: Optional[bytearray]=None) -> None:

        self._verb = verb
        self._path = path
        self._version = version
        self._headers = headers
        self._body = body

    def __repr__(self) -> str:
        return "<Request {0.method} {0.path!r}>".format(self)

    @property
    def method(self) -> str:
        return self._verb.decode()

    @property
    def path(self) -> str:
        return self._path.decode()

    @property
    def headers(self) -> Dict[str, str]:
        if type(self._headers) is bytearray:
            h = {}
            for line in self._headers.splitlines():
                name, value = line.split(b':', 1)

                name = name.decode()
                value = value.decode()

                if value.startswith(' '):
                    value = value[1:]

                h[name] = value

            self._headers = h

        return self._headers

    @property
    def body(self) -> Optional[bytes]:
        if self._body is not None:
            return bytes(self._body)
