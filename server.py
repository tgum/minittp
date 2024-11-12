import socket
import sys
import os
import mimetypes
from pprint import pprint
import re

import chevron

from request import Request
from response import Response

# create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# so it like yk can reuse the same port or smth
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to a public host, and a well-known port
serversocket.bind(("localhost", 8080))
# become a server socket
serversocket.listen(5)

NEWLINE = b"\r\n"

paths = []
def register_handler(path, handler):
	paths.append({"regex": re.compile(path), "handler": handler})

def static_serve(req):
	res = Response()

	path = "www" + req.path
	if path.endswith("/"):
		path += "index.html"

	mime, _ = mimetypes.guess_type(path)
	res.headers["Content-Type"] = f"{mime or 'text/html'}; charset=UTF-8"

	if os.path.isfile(path):
		with open(path, "rb") as f:
			res.body = f.read()
	else:
		with open("www/404.html", "rb") as f:
			res.body = f.read()
			res.status = 404
			res.headers["Content-Type"] = f"{mime}; charset=UTF-8"

	return res

count = 0
def get_counter():
	global count
	count += 1
	return count

def counter_page(req):
	res = Response()
	res.body = str(get_counter())
	return res

def template_serve(req):
	res = Response()
	with open("www/template.html") as f:
		template = f.read()
	res.body = chevron.render(template, {"title": "hi"})
	return res

register_handler(r"^/.+\.html", static_serve)
register_handler(r"^/frog", static_serve)
register_handler(r"^/.*", static_serve)
register_handler(r"^/counter", counter_page)
register_handler(r"^/template", template_serve)

while True:
	print("get connection")
	# accept connections from outside
	(clientsocket, address) = serversocket.accept()
	# now do something with the clientsocket
	
	print("CONNECTION!!!")

	req = Request()
	req.read_socket(clientsocket)

	pprint(req.method)
	pprint(req.path)
	pprint(req.version)
	pprint(req.headers)

	response = None
	for path in reversed(paths):
		if path["regex"].match(req.path):
			print(f"{req.path} matches {path['regex']}")
			response = path["handler"](req)
			if isinstance(response, Response):
				break
		else:
			print(f"{req.path} does not match {path['regex']}")

	print(response)
	response.headers["Server"] = "bascket"
	clientsocket.send(response.get_res_text())
	clientsocket.close()
