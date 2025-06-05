import os
import mimetypes

import chevron

import markdown

import minittp
from minittp import Response

from static_handler import StaticHandler
from minecraft_ping_handler import MinecraftPingHandler

server = minittp.Server("", 8080)


class StaticServe(minittp.RequestHandler):
    def __init__(self):
        pass

    def handler(self, req):
        res = Response()

        path = "www" + req.path

        mime, _ = mimetypes.guess_type(path)
        res.headers["Content-Type"] = f"{mime or 'text/html'}; charset=UTF-8"

        if os.path.isfile(path):
            with open(path, "rb") as f:
                res.body = f.read()
        else:
            return None
        return res


class StaticServeFolder(minittp.RequestHandler):
    def __init__(self, folder, url_prefix=""):
        self.folder = folder
        self.url_prefix = url_prefix

    def handler(self, req):
        res = Response()

        if req.path.startswith(self.url_prefix):
            path = self.folder + req.path[len(self.url_prefix) :]

            mime, _ = mimetypes.guess_type(path)
            res.headers["Content-Type"] = f"{mime or 'text/html'}; charset=UTF-8"

            if os.path.isfile(path):
                with open(path, "rb") as f:
                    res.body = f.read()
            else:
                return None
            return res


class BasicTemplateHandler(minittp.RequestHandler):
    def __init__(self, title, filename):
        self.title = title
        self.filename = filename

    def handler(self, req):
        res = Response()

        with open(f"{self.filename}", "r") as f:
            self.body = f.read()

        with open("templates/page.mustache") as f:
            template = f.read()
        body = chevron.render(self.body, {"bold": lambda a, b: f"<b>{a}</b>"})
        args = {
            "title": self.title,
            "body": body,
        }
        res.body = chevron.render(template, args)
        return res


class TemplateFolder(minittp.RequestHandler):
    def __init__(self, folder, url_prefix=""):
        self.folder = folder
        self.url_prefix = url_prefix

    def handler(self, req):
        print("omg" + req.path)
        res = Response()
        res.headers["Content-Type"] = "text/html; charset=UTF-8"

        if req.path.startswith(self.url_prefix):
            path = self.folder + req.path[len(self.url_prefix) :]

            if os.path.isfile(path):
                with open(path, "r") as f:
                    file_text = f.read().split("\n")

                with open("templates/page.mustache") as f:
                    template = f.read()

                title = file_text[0]
                while title.startswith("-"):
                    title = title[1:]
                body = "\n".join(file_text[1:])

                body = chevron.render(body, {"bold": lambda a, b: f"<b>{a}</b>"})
                args = {
                    "title": title,
                    "body": body,
                }
                res.body = chevron.render(template, args)
                return res
            else:
                return None


class MarkdownHandler(minittp.RequestHandler):
    def __init__(self, folder, url_prefix=""):
        self.folder = folder
        self.url_prefix = url_prefix

    def handler(self, req):
        res = Response()

        if req.path.startswith(self.url_prefix):
            path = self.folder + req.path[len(self.url_prefix) :]

            res.headers["Content-Type"] = "text/html; charset=UTF-8"

            if os.path.isfile(path):
                with open(path, "r") as f:
                    res.body = markdown.markdown(f.read())
                return res
            else:
                return None


class Counter(minittp.RequestHandler):
    def __init__(self):
        self.count = 0

    def handler(self, req):
        res = Response()
        self.count += 1
        res.body = str(self.count)
        return res


server.register_handler(
    r"/index\.html", BasicTemplateHandler("INDEX!", "content/index.html")
)
server.register_handler(r"/mcping/.+(\?.*)?", MinecraftPingHandler())
server.register_handler(r"/.+\.html", TemplateFolder("content"))
server.register_handler(r"/.+\.md", MarkdownHandler("content"))
server.register_handler(r"/500", "error lol")
server.register_handler(r"/page.lol", Counter())

server.register_handler(r"/static/.+", StaticHandler("/static/", "/static/"))

server.internal_redirect(r"/(.*/)?", r"/\1index.html")

server.start()
