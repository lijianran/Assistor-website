
from tornado.httpserver import HTTPServer
from tornado.wsgi import WSGIContainer
from flaskr import create_app
from tornado.ioloop import IOLoop

import win32api
import win32gui

# import setproctitle

# setproctitle.setproctitle('网站服务器')

ct = win32api.GetConsoleTitle()
hd = win32gui.FindWindow(0, ct)
win32gui.ShowWindow(hd, 0)  # 隐藏dos窗口

server = HTTPServer(WSGIContainer(create_app()))
server.listen(5000)
IOLoop.current().start()
