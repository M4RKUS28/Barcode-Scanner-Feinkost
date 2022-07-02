import sys
import mapplication
import mainwindow
import webserver

from PySide2 import QtCore
import pyodbc
import sqlite3
import datetime
# Einstellungen

# Programm Version
PROGRAMM_VERSION: str = "0.9.0"

SQL_DRIVER_USED_VERSION_MS_DRIVER: str = "{ODBC Driver 18 for SQL Server}"
SQL_DRIVER_USED_VERSION_FreeTDS: str = "{FreeTDS}"
SQL_DRIVER_USED_VERSION_FreeTDS_VERSION = 7.4

# Pfad zu lokaler Datenbank, die zum Speichern der Statistiken der Nutzung, sowie der Bewertung dient
local_db_path: str = "./sqlLiteDB.db"
# MS SQL Server mit Daten zu Produkten
ms_sql_server_ip: str = "home.obermui.de"
# MS SQL Server Port
ms_sql_server_port: int = 18769

# Lokaler HTTP SERVER LISTEN IP
local_http_server_ip: str = "0.0.0.0"
# Lokaler HTTP SERVER LISTEN Port
local_http_server_port: int = 8888

# Pfad zu Qt-Designer Formulardatei: Die Grafik wurde nämlich mithilfe des Qt Creators erstellt.
ui_file_path: str = "../src/form_ALT.ui"

item_count_on_web_server_list: int = 50


if __name__ == "__main__":
    print("Programm Start: ", datetime.datetime.now())
    print("-----------------------")
    print("Programm Version: ", PROGRAMM_VERSION)
    print("Python Version: ", sys.version)
    print("Qt Version: ", QtCore.qVersion())
    print("PyODBC Version: ", pyodbc.version)
    print("SQL Lite3 Version: ", sqlite3.version)
    print("Verwendete MS ODBC Driver Version: ", SQL_DRIVER_USED_VERSION_MS_DRIVER)
    print("Verwendete FreeTDS Driver Version: ", SQL_DRIVER_USED_VERSION_FreeTDS, " ",
          SQL_DRIVER_USED_VERSION_FreeTDS_VERSION)
    print("-----------------------\n\n")

    # MApplication
    m_app = None
    # Lokalen Statistiken Server
    w_server = None
    # Rückgabewert QApplication
    ret = None

    try:
        # Starte Lokalen Statistiken Server
        w_server = webserver.Server(local_http_server_ip, local_http_server_port)
        w_server.start_listen()

        # Erstelle Key Press Event Handler und Ui - MainWindow
        m_app = mapplication.MApplication(sys.argv)
        m_win = mainwindow.MainWindow(local_db_path, ms_sql_server_ip, ms_sql_server_port, ui_file_path)

        # connect MApplication ( EventFilter ) with MainWindow( handle_EVENT )
        m_app.newScan.connect(m_win.new_scan)

        # Mache das Fenster sichtbar
        m_win.show()

        # Warte auf exit signal
        ret = m_app.exec_()

    except Exception as exc:
        print(exc)

    # Stoppe lokalen Server und beende das Programm
    w_server.stop_listen()
    sys.exit(ret)