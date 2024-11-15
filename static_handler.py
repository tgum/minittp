import mimetypes
import os

import minittp
from minittp import Response


class StaticHandler(minittp.RequestHandler):
    def __init__(self, url_root, folder_root):
        if url_root.endswith("/"):
            self.folder = True
        else:
            self.folder = False
        self.url = url_root
        self.folder = folder_root

    def handler(self, req):
        res = Response()

        path = self.folder + req.path.removeprefix(self.url)
        print(path)

        path = os.path.normpath(path)
        print(os.path.commonpath([self.folder, path]))
        if not os.path.commonpath([self.folder, path]) + "/" == self.folder:
            return False
        if not os.path.isfile(path[1:]):
            return False

        mime, _ = mimetypes.guess_type(path)
        res.headers["Content-Type"] = f"{mime or 'text/html'}; charset=UTF-8"

        with open(path[1:], "rb") as f:
            res.body = f.read()

        return res
