import struct

def unpack_US(d):
	return struct.unpack(">H", d)

def pack_US(d):
	return struct.pack(">H", d)

def unpack_varint(s):
	d = 0
	for i in range(5):
		b = ord(s.recv(1))
		d |= (b & 0x7F) << 7*i
		if not b & 0x80:
			break
	return d

def pack_varint(d):
	o = b""
	while True:
		b = d & 0x7F
		d >>= 7
		o += struct.pack("B", b | (0x80 if d > 0 else 0))
		if d == 0:
			break
	return o

def unpack_string(s):
	l = unpack_varint(s)
	d = b""
	while len(d) < l:
		d += s.recv(1024)
	return d.decode("utf8")

def pack_string(string):
	o = b""
	o += pack_varint(len(string))
	o += string.encode("utf8")
	return o
	
def pack_data(d):
	o = b""
	o += pack_varint(len(d))
	o += d
	return o
