# from pprint import pprint
import re
import asyncio
import traceback

import chevron

from request import Request
from response import Response

NEWLINE = b"\r\n"


# this is an interface to make async sockets work more like
# normal ones or smth i forgot
class RequestWrapper:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def recv(self, amount=1024):
        return await self.reader.read(amount)

    def write(self, data):
        self.writer.write(data)

    async def drain(self):
        await self.writer.drain()

    async def send(self, data):
        self.write(data)
        await self.drain()

    def close(self):
        self.writer.close()


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.routes = []

    def register_handler(self, path, handler, full_match=True):
        print("register handler")
        if full_match:
            path = f"^{path}$"
        self.routes.append(
            {"type": "handler", "regex": re.compile(path), "handler": handler}
        )

    def internal_redirect(self, path, replacer, full_match=True):
        print("register redirect")
        if full_match:
            path = f"^{path}$"
        self.routes.append(
            {"type": "redirect", "regex": re.compile(path), "replacer": replacer}
        )

    def start(self):
        asyncio.run(self._start())

    async def _start(self):
        server = await asyncio.start_server(self._handle_conn, self.host, self.port)
        print(f"Serving on {self.host}:{self.port}!")

        await self.on_start()

        async with server:
            await server.serve_forever()

    async def on_start(self):
        print("server started!")

    def handler_404(self, req):
        res = Response()
        with open("templates/404.mustache", "r") as f:
            body = f.read()
            res.body = chevron.render(body, {"url": req.path})
            res.status = 404
            res.headers["Content-Type"] = "text/html; charset=UTF-8"
        return res

    def handler_500(self, req, error=""):
        res = Response()
        with open("templates/500.mustache", "r") as f:
            body = f.read()
            res.body = chevron.render(body, {"error": error})
            res.status = 500
            res.headers["Content-Type"] = "text/html; charset=UTF-8"
        return res

    async def _handle_conn(self, reader, writer):
        socket = RequestWrapper(reader, writer)
        print("connection!!!")

        req = Request()
        await req.read_socket(socket)

        print(f"{req.method} {req.path} {req.version}")

        response = None
        for path in reversed(self.routes):
            if path["type"] == "handler":
                if path["regex"].match(req.path):
                    try:
                        response = path["handler"].handler(req)
                    except Exception:
                        error_text = traceback.format_exc()
                        print("\033[41m", end="")
                        print(error_text)
                        print("\033[49m")
                        response = self.handler_500(req, error_text)
                    if isinstance(response, Response):
                        break
            elif path["type"] == "redirect":
                if path["regex"].match(req.path):
                    replaced = path["regex"].sub(path["replacer"], req.path)
                    print(f"-> {req.method} {replaced}")
                    req.path = replaced
        if not isinstance(response, Response):
            response = self.handler_404(req)

        response.headers["Server"] = "bascket"
        await socket.send(response.get_res_text())
        socket.close()
        print("closed")
        print()
