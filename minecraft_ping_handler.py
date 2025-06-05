import socket
import json

import minittp
from minittp import Response

import nbt


class MinecraftPingHandler(minittp.RequestHandler):
	def __init__(self):
		pass

	def handler(self, req):
		res = Response()
		host = req.path.split("/")[-1].split("?")[0]
		port = int(req.query.get("port", [25565])[0])
		print(host, port, req.query)
		
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, port))

		packet = nbt.pack_varint(0) # packet id

		packet += nbt.pack_varint(770) # protocol version
		packet += nbt.pack_string(host) # host
		packet += nbt.pack_US    (port) # port
		packet += nbt.pack_varint(1) # next state

		packet = nbt.pack_data(packet)

		s.send(packet)
		s.send(nbt.pack_data(nbt.pack_varint(0)))
		print("sent packet")

		nbt.unpack_varint(s) # packet len
		nbt.unpack_varint(s) # packet id

		data = json.loads(nbt.unpack_string(s))

		s.close()
		
		players = "\n".join([f"<li>{player["name"]}</li>" for player in data["players"]["sample"]])
		
		res.body = f"""
		<h1>pinging {host}:{port}</h1>
		version: {data["version"]["name"]} <br>
		icon: <img src="{data["favicon"]}">
		<h3>players</h3>
		online: {data["players"]["online"]}/{data["players"]["max"]}<br>
		<ul>
		{players}
		</ul>
		"""
		
		return res
