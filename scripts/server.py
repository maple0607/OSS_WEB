#coding:utf-8
import sys

from application import applicaton, Application
from tornado.httpserver import HTTPServer
from tornado.options import define, options
from tornado.ioloop import IOLoop
define("port", default=8280, help="run on th given port", type=int)
def main():
    options.parse_command_line()
    ltnPort = options.port
    if len(sys.argv) > 1:
    	ltnPort = sys.argv[1]
    applicaton = Application(ltnPort)
    IOLoop.instance().start()

if __name__ == "__main__":
    main()