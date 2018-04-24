from os import stat
import  socket

class MiniWebSrv :

    _indexPages = ["index.html"]

    _mimeTypes = {
        ".htm"   : "text/html;charset=utf-8",
        ".html"  : "text/html;charset=utf-8",
        ".css"   : "text/css;charset=utf-8",
        ".csv"   : "text/csv;charset=utf-8",
        ".js"    : "application/javascript;charset=utf-8",
        ".xml"   : "application/xml;charset=utf-8",
        ".json"  : "application/json;charset=utf-8",
        ".zip"   : "application/zip",
        ".jpg"   : "image/jpeg",
        ".jpeg"  : "image/jpeg",
        ".png"   : "image/png",
        ".gif"   : "image/gif",
        ".svg"   : "image/svg+xml;charset=utf-8",
        ".ico"   : "image/x-icon"
    }

    def __init__( self,
                  routeHandlers = None,
                  port          = 80,
                  bindIP        = '0.0.0.0',
                  webPath       = 'www' ) :
        self._routeHandlers = routeHandlers
        self._srvAddr = (bindIP, port)
        self._webPath = webPath
        self._started = False


    def _fileExists(self, path) :
        try :
            stat(path)
            return True
        except :
            return False

    def _unquote(self, s) :
        arr = s.split('%')
        arr2 = [bytes((int(x[:2],16),)) + x[2:].encode() for x in arr[1:]]
        return arr[0] + b''.join(arr2).decode()

    def start(self) :
        if not self._started:
            self._server = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
            try:
                self._server.bind(self._srvAddr)
                print("Server started.")
            except Exception as e:
                print("Error: Could not bind to port.")

            self._server.listen(1)
            self._started = True
        else:
            print("WebServer already started.")

    def accept(self):
        try:
            self._server.setblocking(False)
            client, cliAddr = self._server.accept()
            self._server.setblocking(True)
            return client, cliAddr
        except:
            return None, None

    def stop(self):
        if self._started:
            self._server.close()
            self._started = False
            print("WebServer stoped.")
        else:
            print("WebServer already stopped")
        
    @property
    def started(self):
        return self._started
        
    def GetMimeTypeFromFilename(self, filename) :
        filename = filename.lower()
        for ext in self._mimeTypes :
            if filename.endswith(ext) :
                return self._mimeTypes[ext].encode()
        return None


    def GetRouteHandler(self, resUrl, method) :
        if self._routeHandlers :
            resUrl = resUrl.upper()
            method = method.upper()
            for route in self._routeHandlers :
                if len(route) == 3 and            \
                   route[0].upper() == resUrl and \
                   route[1].upper() == method :
                   return route[2]
        return None


    def _physPathFromURLPath(self, urlPath) :
        if urlPath == '/' :
            for idxPage in self._indexPages :
            	physPath = self._webPath + '/' + idxPage
            	if self._fileExists(physPath) :
            		return physPath
        else :
            physPath = self._webPath + urlPath
            if self._fileExists(physPath) :
                return physPath
        return None

    def handle_client(self, c_socket, address):
        try:
        #if True:
            _headers = { }
            _method = None
            _path = None
            _httpVer = None
            _resPath = '/'
            request_data = {}

            c_socket.settimeout(2)

            # first line parse
            elements = c_socket.readline().decode().strip().split()
            if len(elements) == 3 :
                _method = elements[0].upper()
                _path = elements[1]
                _httpVer = elements[2].upper()
                elements = _path.split('?', 1)
                if len(elements) > 0 :
                    _resPath = elements[0]
            else:
                """method Not support"""
                c_socket.sendall(b'HTTP/1.1 405 Method Not Allowed\n')
                c_socket.sendall(b'Content-Type: text/html;charset=utf-8\n')
                c_socket.sendall(b'Connection: close\n\n')
                c_socket.sendall(b"<html><body><center><h1>Error 405: Method Not Allowed</h1></center><p>Head back to <a href=\"/\">dry land</a>.</p></body></html>")
                print("405 Method not allowed")
                c_socket.close()
                return

            # head parse
            while True :
                elements = c_socket.readline().decode().strip().split(':', 1)
                if len(elements) == 2 :
                    _headers[elements[0].strip()] = elements[1].strip()
                elif len(elements) == 1 and len(elements[0]) == 0 :
                    if _method == 'POST':
                        _contentType = _headers.get("Content-Type", None)
                        _contentLength = int(_headers.get("Content-Length", 0))
                    break

            print("Request:\nmethod:{b}\npath:{c}\nheaders:{d}".format(b=_method,c=_resPath,d=_headers))

            # Post request data parse
            if _method == 'POST':
                c_socket.setblocking(False)
                b = None
                try :
                    b = c_socket.read(_contentLength)
                except :
                    pass
                c_socket.settimeout(2)

                if b and len(b) > 0 :
                    elements = b.decode().split('&')
                    for s in elements :
                        param = s.split('=', 1)
                        if len(param) > 0 :
                            value = self._unquote(param[1]) if len(param) > 1 else ''
                            request_data[self._unquote(param[0])] = value
                print("Posted request data:\n{len}\n{ori}\n{data}".format(len=_contentLength, ori=b.decode(),data=request_data))


            routeHandler = self.GetRouteHandler(_resPath, _method)
            if routeHandler:
                routeHandler(c_socket, request_data)
            elif _method=='GET':
                filepath = self._physPathFromURLPath(_resPath)
                if filepath:
                    contentType = self.GetMimeTypeFromFilename(filepath)
                    if contentType:
                        """WriteResponseFile"""
                        c_socket.sendall(b'HTTP/1.1 200 OK\n')
                        c_socket.sendall(b'Content-Type: ' + contentType + b'\n')
                        c_socket.sendall(b'Connection: close\n\n')

                        size = stat(filepath)[6]
                        if size > 0:
                            BUF_SIZE = 1024
                            buf = bytearray(BUF_SIZE)
                            with open(filepath,'rb') as file:
                                while size > 0:
                                    x =file.readinto(buf)
                                    if x<len(buf):
                                        buf = memoryview(buf)[:x]
                                    #used in cpython: y = c_socket.send(buf)
                                    y = c_socket.sendall(buf)
                                    size -= x
                                file.close()
                    else:
                        """file ext not supported"""
                        c_socket.sendall(b'HTTP/1.1 403 Forbidden\n')
                        c_socket.sendall(b'Content-Type: text/html;charset=utf-8\n')
                        c_socket.sendall(b'Connection: close\n\n')
                        c_socket.sendall(b"<html><body><center><h1>Error 403: File forbiddened</h1></center><p>Head back to <a href=\"/\">dry land</a>.</p></body></html>")
                        print("403 Forbidden")
                else:
                    """cann't find the file"""
                    c_socket.sendall(b'HTTP/1.1 404 File not found\n')
                    c_socket.sendall(b'Content-Type: text/html;charset=utf-8\n')
                    c_socket.sendall(b'Connection: close\n\n')
                    c_socket.sendall(b"<html><body><center><h1>Error 404: File not found</h1></center><p>Head back to <a href=\"/\">dry land</a>.</p></body></html>")
                    print("404 File not found")
            else:
                """method Not support"""
                c_socket.sendall(b'HTTP/1.1 405 Method Not Allowed\n')
                c_socket.sendall(b'Content-Type: text/html;charset=utf-8\n')
                c_socket.sendall(b'Connection: close\n\n')
                c_socket.sendall(b"<html><body><center><h1>Error 405: Method Not Allowed</h1></center><p>Head back to <a href=\"/\">dry land</a>.</p></body></html>")
                print("405 Method not allowed")

            c_socket.close()
        except:
            pass
