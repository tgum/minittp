import urllib.parse

NEWLINE = b"\r\n"


class Request:
    def __init__(self):
        self.method = "GET"
        self.path = "/"
        self.version = "HTTP/1.1"
        self.headers = {}
        self.body = ""
        self.query = {}

    async def read_socket(self, sock):
        """
        idk if this is the right place to put this function
        but maybe someday ill rewrite it so im not gonna touch it
        it basically takes a socket and reads a request
        currently does not handle if the request has like data which is not headers
        basically post requests
        """
        buffer = b""
        state = "status"
        recieved = None  # maybe this optimisizefdes it idk
        while True:
            recieved = await sock.recv(1)
            buffer += recieved
            if buffer.endswith(NEWLINE):
                buffer = buffer[:-2]
                if buffer == b"":
                    if "Content-Length" in self.headers:
                        pass
                    break
                elif state == "status":
                    status = buffer.split(b" ")
                    self.method = status[0].decode()
                    self.path = status[1].decode()
                    self.version = status[2].decode()
                    state = "headers"

                elif state == "headers":
                    chars_since_value = -1
                    header_name = ""
                    header_value = ""
                    for char in buffer.decode("ascii"):
                        char = char
                        if chars_since_value == -1:
                            if char == ":":
                                chars_since_value = 0
                            else:
                                header_name += char
                        else:
                            if chars_since_value == 0:
                                if char != " ":
                                    chars_since_value += 1
                            if chars_since_value > 0:
                                header_value += char
                    self.headers[header_name] = header_value

                buffer = b""
        parsed = urllib.parse.urlparse(self.path)
        self.query = urllib.parse.parse_qs(parsed.query)
