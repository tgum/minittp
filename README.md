# minittp

minittp is a small web web server written in python.

It lets you define handlers for different URLs and stuff

Example:

```python
# import the module
import minittp
from minittp import Response

# first arg is the domain or smth, second is the port
server = minittp.Server("", 8080)

# For now handlers need to be a class
class Counter(minittp.RequestHandler):
    # handlers can have some state
    def __init__(self):
        self.count = 0

    # this function returns a Response, if it returns anything else its a 404
    def handler(self, req):
        res = Response()
        self.count += 1
        res.body = str(self.count)
        return res

# the URL pattern is a regex
server.register_handler(r"/counter", Counter())

server.start()
```

TODO:

- [ ] #3
- [ ] #2
- [ ] #1
- [ ] #4
