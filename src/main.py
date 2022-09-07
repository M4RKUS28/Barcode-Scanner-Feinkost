import mapplication
import mainwindow
import webserver
import logger
# Für Informationsausgabe

import datetime
import os
import sys

import constants as consts

import logging
from pathlib import Path
log = logging.getLogger(Path(__file__).name)


if __name__ == "__main__":
    # Change Working Directory to the one this file is in
    abspath = os.path.abspath(__file__)
    d_name = os.path.dirname(abspath)
    os.chdir(d_name)

    # Tee stderr to log and to console
    try:
        logger.setup(consts.log_file_path)
    except Exception as e:
        print("Failed to setup Logger: {0}".format(e))
        sys.exit(99)

    # Wenn --help aufgerufen wird, gib kurze Information aus
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            log.debug(sys.argv)
            print("Mit diesem Programm sollen Kunden durch das Scannen eines Produkt Bar Codes zusätzliche "
                  "Informationen zu diesem über die JTL-Wawi MS SQL Datenbank bekommen.")
            print("Mit '", sys.argv[0], " -platform off-screen' können sie das Programm ohne Fenster starten")
            exit()

    # Print All Versions and write it also to log
    logger.print_debug_versions()

    # MApplication
    m_app: mapplication = None
    # Lokalen Statistiken Server
    w_server: webserver = None
    # Rückgabewert QApplication
    ret: int = 0
    m_win: mainwindow = None

    try:
        # Starte Lokalen Statistiken Server
        w_server = webserver.Server(consts.local_http_server_ip, consts.local_http_server_port)
        w_server.start_listen()

        # Erstelle Key Press Event Handler und Ui - MainWindow
        m_app = mapplication.MApplication(sys.argv)
        m_win = mainwindow.MainWindow(consts.local_db_path, consts.ui_file_path)

        # connect MApplication ( EventFilter ) with MainWindow( handle_EVENT )
        m_app.newScan.connect(m_win.new_scan)

        # Mache das Fenster sichtbar
        m_win.show()

        # Warte auf exit signal
        ret = m_app.exec_()

        m_win.cleanUp()

    except Exception as exc:
        log.critical("\nError: Critical: {0}".format(exc))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        log.critical(" -> ERROR TYPE: {0}, FILE: {1}, LINE: {2}".format(exc_type, os.path.split(
                                                                         exc_tb.tb_frame.f_code.co_filename)[1],
                                                                        exc_tb.tb_lineno))
        if ret == 0:
            ret = -1

    # Stoppe lokalen Server und beende das Programm
    w_server.stop_listen()
    log.info("-> exit({0}) -> Programm Stop um: {1}"
             "\n--------------------------------------------------------------------------------"
             .format(ret, datetime.datetime.now()))

    logger.cleanup()
    sys.exit(ret)
