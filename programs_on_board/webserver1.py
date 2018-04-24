from MiniWebSrv import MiniWebSrv

webserver = MiniWebSrv()
webserver.start()

while True:
    client, cliAddr = webserver.accept()
    if client:
        webserver.handle_client(client, cliAddr)
