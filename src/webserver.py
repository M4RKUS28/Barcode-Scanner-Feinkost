import logging
import ssl
from http.server import ThreadingHTTPServer
from pathlib import Path

from PySide6.QtCore import QThread

import constants
from requesthandler import RequestHandler

log = logging.getLogger(Path(__file__).name)


# Lokaler einfacher Webserver, um Statistiken zur Nutzung angezeigt zu bekommen
class Server(QThread):
    # Attribute
    listenPort: int = -1
    listenIP: str = ""

    # Objekte
    webserver: ThreadingHTTPServer = None

    # Konstruktor: Erstelle Server
    def __init__(self, l_ip, l_port):
        super().__init__()
        self.listenIP = l_ip
        self.listenPort = l_port

    # Starte Server in extra Thread
    def start_listen(self):
        self.start()

    # Stoppe Server und warte auf Beenden des Threads
    def stop_listen(self):
        log.info("[WEBSERVER]: Stoppe Webserver....")
        if self.webserver:
            self.webserver.shutdown()
        self.wait()

    # Thread - Funktion: Server wartet auf eingehende TCP Verbindungen und erstellt für jede einen
    # Thread mit einem RequestHandler
    def run(self):
        log.info("[WEBSERVER]: Starte Webserver....")

        with ThreadingHTTPServer((self.listenIP, self.listenPort), RequestHandler) as server:
            if constants.ENABLE_SSL:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(certfile=constants.CERT_PATH)
                server.socket = context.wrap_socket(server.socket, server_side=True)
            self.webserver = server
            log.info("[WEBSERVER]: Warte auf Verbindungen....")
            server.serve_forever()
        log.info("[WEBSERVER]: Webserver beendet.")
        return None
