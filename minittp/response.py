from http import HTTPStatus

NEWLINE = b"\r\n"


def stob(string):
    """turns either str or bytes to bytes"""
    if type(string) is str:
        return string.encode("ascii")
    if type(string) is bytes:
        return string
    print(string, type(string))
    raise Exception("idk what to do")


class Response:
    def __init__(self):
        self.status = 200
        self.headers = {}
        self.headers["Content-Type"] = "text/html; charset=UTF-8"
        self.body = ""

    def get_res_text(self):
        """
        returns the string which represents the response
        """
        self.headers["Content-Length"] = len(self.body)

        result = (
            stob(f"HTTP/1.1 {str(self.status)} {HTTPStatus(self.status).phrase}")
            + NEWLINE
        )
        for header in self.headers:
            result += stob(f"{header}: {self.headers[header]}") + NEWLINE
        result += stob("") + NEWLINE
        if type(self.body) is str:
            result += self.body.encode()
        else:
            result += self.body
        result += NEWLINE

        return result
