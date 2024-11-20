from . import request
from . import response
from . import minittp


def hello():
    print("ello mate")


Response = response.Response
Server = minittp.Server
RequestHandler = minittp.RequestHandler
