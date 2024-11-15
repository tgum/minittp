# minittp

minittp is a small web web server written in python.

It lets you define handlers for different URLs and stuff

Example:

```python
# import the module
import minittp
from minittp import Response

server = minittp.Server("", 8080)

# For now handlers need to be a class
class Counter(minittp.RequestHandler):
    def __init__(self):
        self.count = 0

    def handler(self, req):
        res = Response()
        self.count += 1
        res.body = str(self.count)
        return res


server.register_handler(r"/counter", Counter())

server.start()
```
