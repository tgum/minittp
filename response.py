NEWLINE = b"\r\n"

# im loading the names for the response codes
# idk if i need them but ehhhhh
response_codes = {}
with open("response_codes.csv") as f:
	for line in f.readlines():
		split_line = line.split(",")
		# if grouda[0] in response_codes:
		# 	print(f"{line} is a duplicate")
		response_codes[int(split_line[0])] = split_line[1][:-1]

def stob(string):
	"""turns either str or bytes to bytes"""
	if type(string) == str:
		return string.encode("ascii")
	if type(string) == bytes:
		return string
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

		result  = stob(f"HTTP/1.1 {str(self.status)} {response_codes[self.status]}") + NEWLINE
		for header in self.headers:
			result += stob(f"{header}: {self.headers[header]}") + NEWLINE
		result += stob(f"") + NEWLINE
		if type(self.body) == str:
			result += self.body.encode()
		else:
			result += self.body
		result += NEWLINE

		return result