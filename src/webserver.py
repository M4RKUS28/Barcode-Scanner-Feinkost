import sys
import calendar
import shutil
import re

from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler  # , HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime, timedelta
from threading import Thread

import settings
import localdatabasemanager

import logging
from pathlib import Path

log = logging.getLogger(Path(__file__).name)


# Lokaler einfacher Webserver, um Statistiken zur Nutzung angezeigt zu bekommen
class Server:
    # Attribute
    listenPort: int = -1
    listenIP: str = ""

    # Objekte
    webserver: ThreadingHTTPServer = None
    thread: Thread = None

    # Konstruktor: Erstelle Server
    def __init__(self, l_ip, l_port):
        self.listenIP = l_ip
        self.listenPort = l_port
        try:
            self.thread = Thread(target=self.run_web_server, args=())
        except Exception as exc:
            log.critical("> Webserver erstellen ist fehlgeschlagen: {0}".format(exc))
            sys.exit(12)

    # Starte Server in extra Thread
    def start_listen(self):
        self.thread.start()

    # Stoppe Server und warte auf Beenden des Threads
    def stop_listen(self):
        if self.webserver:
            self.webserver.shutdown()
        self.thread.join(10)

    # Thread - Funktion: Server wartet auf eingehende TCP Verbindungen und erstellt für jede einen
    # Thread mit einem RequestHandler
    def run_web_server(self):
        with ThreadingHTTPServer((self.listenIP, self.listenPort), RequestHandler) as server:
            self.webserver = server
            server.serve_forever()
        return None


# Klasse, die eine TCP Verbindung managed
class RequestHandler(BaseHTTPRequestHandler):
    # class RequestHandler(SimpleHTTPRequestHandler):
    # Objekte
    loc_db_mngr = None

    # HTTP Methode um Internetseitenquelltext zu bekommen:
    def do_GET(self):
        # Stelle Verbindung mit lokaler Datenbank her, um Statistiken auslesen zu können
        self.loc_db_mngr = localdatabasemanager.LocalDataBaseManager()
        self.loc_db_mngr.connect(settings.local_db_path)

        # Standard HTTP Sende-Status
        html_status = 200
        html_string: str = ""
        try:
            if self.path == "/style.css":
                self.send_response(200)
                self.send_header('content-type', 'text/css')
                self.end_headers()

                # Open the file, read bytes, serve
                with open("../html/css/style.css", 'rb') as file:
                    bts = file.read()
                if not self.tryWriteOK(bts):
                    self.loc_db_mngr = None
                    return
                return

            # Je nach URL Pfad / je nach aufgerufener Internetseite:
            sub_paths = self.path.split("/")
            if sub_paths is not None and len(sub_paths) > 1:
                if sub_paths[1] == "monatsstatus.html":
                    # Lade HTML TEMPLATE für Monatsstatus mit Javascript Chart
                    html_string = open("../html/monatsstatus.html", "r").read()
                    now = datetime.now()
                    days_of_month = calendar.monthrange(now.year, now.month)[1]
                    day_of_month = int(now.strftime("%d")) - 1

                    scan_list = [0] * days_of_month
                    for day in range(0, day_of_month + 1):
                        current_day = datetime.today().date() - timedelta(days=day)
                        scan_list[day_of_month - day] = self.loc_db_mngr.count_scans_at_date(current_day)[0][0]
                    html_string = html_string.replace("%DATA_DATA_SET_1%", str(scan_list))

                    label_list = [""] * days_of_month
                    for i in range(0, days_of_month):
                        label_list[i] = str(i + 1) + "."
                    html_string = html_string.replace("%DATA_LABEL_SET_1%", str(label_list))

                elif sub_paths[1] == "monatsstatus-hersteller.html":
                    # Lade HTML TEMPLATE für Wochenstatus mit Javascript Chart
                    html_string = open("../html/monatsstatus-hersteller.html", "r").read()

                    now = datetime.now()
                    days_of_month = calendar.monthrange(now.year, now.month)[1]
                    day_of_month = int(now.strftime("%d")) - 1

                    replace_str: str = ""
                    herstellerlist = self.loc_db_mngr.getHerstellerList()

                    for i in range(0, len(herstellerlist)):
                        if herstellerlist[i] is None:
                            continue
                        elif herstellerlist[i][0] is None:
                            hersteller = "Unbekannt"
                        else:
                            hersteller = herstellerlist[i][0]

                        scan_list = [0] * days_of_month
                        for day in range(0, day_of_month + 1):
                            current_day = datetime.today().date() - timedelta(days=day)
                            buf = self.loc_db_mngr.count_scans_at_date_where_hersteller_is(current_day, hersteller)
                            if buf is not None:
                                scan_list[day_of_month - day] = buf[0][0]

                        if replace_str != "":
                            replace_str += ","
                        replace_str += "{\r\n" \
                                       + "     label: '" + hersteller + "',\r\n" \
                                       + "     data: " + str(scan_list) + ",\r\n" \
                                       + "     backgroundColor: [\r\n" \
                                       + "         'rgba(" + str((i * 50) % 200) + ", " + \
                                       str((i * 100) % 200) + ", " + \
                                       str((i * 150) % 200) + ", 0.2)'\r\n" \
                                       + "     ],\r\n" \
                                       + "    borderColor: [\r\n" \
                                       + "         'rgba(" + str((i * 50) % 200) + ", " + \
                                       str((i * 100) % 200) + ", " + \
                                       str((i * 150) % 200) + ", 1)'\r\n" \
                                       + "     ],\r\n" \
                                       + "     borderWidth: 2\r\n" \
                                       + "}"

                    html_string = html_string.replace("%DATA_DATA_SETS%", replace_str)

                    label_list = [""] * days_of_month
                    for i in range(0, days_of_month):
                        label_list[i] = str(i + 1) + "."
                    html_string = html_string.replace("%DATA_LABEL_SET%", str(label_list))

                elif sub_paths[1] == "monatsstatus-kategorie.html":
                    # Lade HTML TEMPLATE für Wochenstatus mit Javascript Chart
                    html_string = open("../html/monatsstatus-kategorie.html", "r").read()

                    now = datetime.now()
                    days_of_month = calendar.monthrange(now.year, now.month)[1]
                    day_of_month = int(now.strftime("%d")) - 1

                    replace_str: str = ""
                    kategorieList = self.loc_db_mngr.getKategorieList()

                    for i in range(0, len(kategorieList)):
                        if kategorieList[i] is None:
                            continue
                        elif kategorieList[i][0] is None:
                            kategorie = "Unbekannt"
                        else:
                            kategorie = kategorieList[i][0]

                        scan_list = [0] * days_of_month
                        for day in range(0, day_of_month + 1):
                            current_day = datetime.today().date() - timedelta(days=day)
                            buf = self.loc_db_mngr.count_scans_at_date_where_kategorie_is(current_day, kategorie)
                            if buf is not None:
                                scan_list[day_of_month - day] = buf[0][0]

                        if replace_str != "":
                            replace_str += ","
                        replace_str += "{\r\n" \
                                       + "     label: '" + kategorie + "',\r\n" \
                                       + "     data: " + str(scan_list) + ",\r\n" \
                                       + "     backgroundColor: [\r\n" \
                                       + "         'rgba(" + str((i * 50) % 200) + ", " + \
                                       str((i * 100) % 200) + ", " + \
                                       str((i * 150) % 200) + ", 0.2)'\r\n" \
                                       + "     ],\r\n" \
                                       + "    borderColor: [\r\n" \
                                       + "         'rgba(" + str((i * 50) % 200) + ", " + \
                                       str((i * 100) % 200) + ", " + \
                                       str((i * 150) % 200) + ", 1)'\r\n" \
                                       + "     ],\r\n" \
                                       + "     borderWidth: 2\r\n" \
                                       + "}"

                    html_string = html_string.replace("%DATA_DATA_SETS%", replace_str)

                    label_list = [""] * days_of_month
                    for i in range(0, days_of_month):
                        label_list[i] = str(i + 1) + "."
                    html_string = html_string.replace("%DATA_LABEL_SET%", str(label_list))

                elif sub_paths[1] == "wochenstatus.html":
                    # Lade HTML TEMPLATE für Wochenstatus mit Javascript Chart
                    html_string = open("../html/wochenstatus.html", "r").read()
                    scan_list = [0] * 7
                    weekday = datetime.today().weekday()
                    for day in range(0, weekday + 1):
                        current_day = datetime.today().date() - timedelta(days=day)
                        buf = self.loc_db_mngr.count_scans_at_date(current_day)
                        if buf is not None:
                            scan_list[weekday - day] = buf[0][0]
                    html_string = html_string.replace("%DATA_DATA_SET_1%", str(scan_list))

                elif sub_paths[1] == "wochenstatus-hersteller.html":
                    # Lade HTML TEMPLATE für Wochenstatus mit Javascript Chart
                    html_string = open("../html/wochenstatus-hersteller.html", "r").read()
                    replace_str: str = ""
                    weekday = datetime.today().weekday()

                    herstellerlist = self.loc_db_mngr.getHerstellerList()

                    for i in range(0, len(herstellerlist)):
                        if herstellerlist[i] is None:
                            continue
                        elif herstellerlist[i][0] is None:
                            hersteller = "Unbekannt"
                        else:
                            hersteller = herstellerlist[i][0]

                        scan_list = [0] * 7
                        for day in range(0, weekday + 1):
                            current_day = datetime.today().date() - timedelta(days=day)
                            buf = self.loc_db_mngr.count_scans_at_date_where_hersteller_is(current_day,
                                                                                           hersteller)
                            if buf is not None:
                                scan_list[weekday - day] = buf[0][0]
                        if replace_str != "":
                            replace_str += ","
                        replace_str += "{\r\n" \
                                       + "     label: '" + hersteller + "',\r\n" \
                                       + "     data: " + str(scan_list) + ",\r\n" \
                                       + "     backgroundColor: [\r\n" \
                                       + "         'rgba(" + str((i * 50) % 200) + ", " + \
                                       str((i * 100) % 200) + ", " + \
                                       str((i * 150) % 200) + ", 0.2)'\r\n" \
                                       + "     ],\r\n" \
                                       + "    borderColor: [\r\n" \
                                       + "         'rgba(" + str((i * 50) % 200) + ", " + \
                                       str((i * 100) % 200) + ", " + \
                                       str((i * 150) % 200) + ", 1)'\r\n" \
                                       + "     ],\r\n" \
                                       + "     borderWidth: 2\r\n" \
                                       + "}"

                    html_string = html_string.replace("%DATA_DATA_SETS%", replace_str)

                elif sub_paths[1] == "jahresstatus.html":
                    # Lade HTML TEMPLATE für Jahresstatus mit Javascript Chart
                    html_string = open("../html/jahresstatus.html", "r").read()
                    scan_list = [0] * 12
                    s_list = self.loc_db_mngr.get_all_scans()
                    current_year = datetime.now().year

                    for m in range(1, 13):
                        for scan in s_list:
                            scan_d = datetime.fromisoformat(scan[1])
                            if scan_d.year == current_year and scan_d.month == m:
                                scan_list[m - 1] += 1
                    html_string = html_string.replace("%DATA_DATA_SET_1%", str(scan_list))

                elif sub_paths[1] == "jahresstatus-hersteller.html":

                    # Lade HTML TEMPLATE für Jahresstatus mit Javascript Chart
                    html_string = open("../html/jahresstatus-hersteller.html", "r").read()
                    replace_str: str = ""
                    current_year = datetime.now().year

                    s_list = self.loc_db_mngr.get_all_scans()
                    herstellerlist = self.loc_db_mngr.getHerstellerList()
                    for i in range(0, len(herstellerlist)):
                        if herstellerlist[i] is None:
                            continue
                        elif herstellerlist[i][0] is None:
                            hersteller = "Unbekannt"
                        else:
                            hersteller = herstellerlist[i][0]

                        ####
                        # DRINGEND MIT SQL STATEMENT SCHNELLER MACHEN!!!!!!
                        ####
                        scan_list = [0] * 12
                        for m in range(1, 13):
                            for scan in s_list:
                                scan_d = datetime.fromisoformat(scan[1])
                                if scan_d.year == current_year and scan_d.month == m:
                                    if scan[5] is None and hersteller == "Unbekannt":
                                        scan_list[m - 1] += 1
                                    elif scan[5] == hersteller:
                                        scan_list[m - 1] += 1

                        if replace_str != "":
                            replace_str += ","
                        replace_str += "{\r\n" \
                                       + "     label: '" + hersteller + "',\r\n" \
                                       + "     data: " + str(scan_list) + ",\r\n" \
                                       + "     backgroundColor: [\r\n" \
                                       + "         'rgba(" + str((i * 50) % 200) + ", " + \
                                       str((i * 100) % 200) + ", " + \
                                       str((i * 150) % 200) + ", 0.2)'\r\n" \
                                       + "     ],\r\n" \
                                       + "    borderColor: [\r\n" \
                                       + "         'rgba(" + str((i * 50) % 200) + ", " + \
                                       str((i * 100) % 200) + ", " + \
                                       str((i * 150) % 200) + ", 1)'\r\n" \
                                       + "     ],\r\n" \
                                       + "     borderWidth: 2\r\n" \
                                       + "}"

                    html_string = html_string.replace("%DATA_DATA_SETS%", replace_str)

                # Erweiterbar mit tabelle/INDEX, mit immer nur 100 Items auf einer seite mit nächster
                #  seite und 1 seite zurück gg. mit POST die anzahl umstellbar machen!
                elif sub_paths[1] == "tabelle":
                    if len(sub_paths) < 3 or not sub_paths[2].isdigit():
                        html_string = open("../html/404.html", "r").read()
                        html_status = 404
                    else:
                        html_string = open("../html/tabelle.html", "r").read()
                        page: int = int(sub_paths[2])
                        page_count: int = int(self.loc_db_mngr.getItemCount() /
                                              settings.item_count_on_web_server_list)
                        html_string = html_string.replace("%LAST%", str(page_count))
                        html_string = html_string.replace("%CURRENT%", str(page))

                        if page == page_count:
                            html_string = html_string.replace("%NEXT%\">></a>", "%NEXT%\"></a>")
                            html_string = html_string.replace("%NEXT%", str(page))
                        else:
                            html_string = html_string.replace("%NEXT%", str(page + 1))
                        if page == 0:
                            html_string = html_string.replace("%BACK%\"><</a>", "%BACK%\"></a>")
                            html_string = html_string.replace("%BACK%", str("0"))
                        else:
                            html_string = html_string.replace("%BACK%", str(page - 1))

                        s_list = self.loc_db_mngr.getRange(settings.item_count_on_web_server_list * page,
                                                           settings.item_count_on_web_server_list)
                        send_data = ""
                        for scan in s_list:
                            send_data += """<tr>\n
                                                <td>{0}</td>\n
                                                <td>{1}</td>\n
                                                <td>{2}</td>\n
                                                <td>{3}</td>\n
                                                <td>{4}</td>\n
                                                <td>{5}</td>\n
                                                <td>{6}</td>\n
                                        </tr>\n""".format(scan[0], scan[1], scan[2], scan[3], scan[4], scan[5], scan[6])
                        html_string = html_string.replace("%LINES%", send_data)
                elif sub_paths[1] == "":
                    html_string = open("../html/main.html", "r").read()
                elif sub_paths[1] == "settings.html":
                    html_string = open("../html/settings.html", "r").read()
                    html_string = self.replaceVarsInSettingsHtml(html_string)
                elif sub_paths[1] == "images":
                    if len(sub_paths) == 3:
                        if sub_paths[2] == "reload.png":
                            self.send_response(200)
                            self.send_header('content-type', 'image/png')
                            self.end_headers()
                            with open("../images/reload.png", 'rb') as file_handle:
                                bts: bytes = file_handle.read()
                            self.tryWriteOK(bts)
                            return
                        elif sub_paths[2] == "favicon.ico":
                            self.send_response(200)
                            self.send_header('content-type', 'image/x-icon')
                            self.end_headers()
                            with open("../images/favicon.ico", 'rb') as file_handle:
                                bts: bytes = file_handle.read()
                            self.tryWriteOK(bts)
                            return
                        elif sub_paths[2] == "background.png":
                            self.send_response(200)
                            self.send_header('content-type', 'image/png')
                            self.end_headers()
                            with open("../images/background.jpg", 'rb') as file_handle:
                                bts: bytes = file_handle.read()
                            self.tryWriteOK(bts)
                            return
                        else:
                            log.debug("> WARNUNG: Seite nicht gefunden: {0}".format(self.path))
                            html_string = open("../html/404.html", "r").read()
                            html_status = 404
                elif sub_paths[1] == "favicon.ico":
                    self.send_response(200)
                    self.send_header('content-type', 'image/x-icon')
                    self.end_headers()
                    with open("../images/favicon.ico", 'rb') as file_handle:
                        bts: bytes = file_handle.read()
                    self.tryWriteOK(bts)
                    return

                elif sub_paths[1] == "log.html":
                    html_string = open("../html/log.html", "r").read()
                    text: str = ""
                    with open(settings.log_file_path, "r") as file:
                        last: str = ""
                        for line in file:
                            text += "<p "
                            if "DEBUG:" in line:
                                last = "name=\"debug\" style=\"display: none; color: gray\""
                                text += last
                            elif "INFO:" in line:
                                last = "name=\"info\" style=\"color: black;\""
                                text += last
                            elif "WARNING:" in line:
                                last = "name=\"warning\" style=\"color: orange;\""
                                text += last
                            elif "ERROR:" in line:
                                last = "name=\"error\" style=\"color: red;\""
                                text += last
                            elif "CRITICAL:" in line:
                                last = "name=\"critical\" style=\"color: red;\""
                                text += last
                            elif "-----------------------------------------------------" in line:
                                last = ""
                            else:
                                text += last
                            text += ">" + line.rstrip() + "</p>\n"
                    html_string = html_string.replace("%DATA%", text)
                else:
                    log.debug("> WARNUNG: Seite nicht gefunden: {0}".format(self.path))
                    html_string = open("../html/404.html", "r").read()
                    html_status = 404

            self.send_response(html_status)
            self.send_header('content-type', 'text/html; charset=utf-8')
            self.end_headers()

            # Write Funktion in eigenem try-catch statement, um Html-Fehler senden zu können, wenn im SQL Teil
            # etwas fehlschlägt!
            if not self.tryWriteOK(html_string.encode("utf-8")):
                self.loc_db_mngr = None
                return

        except Exception as exc:
            log.error("> Es ist ein Fehler im RequestHandler aufgetreten: {0}".format(exc))
            self.send_response(500)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.tryWriteOK("<h1>Ein unerwartetes Problem ist aufgetreten!</h1>".encode("utf-8"))

        self.loc_db_mngr = None
        return

    @staticmethod
    def replaceVarsInSettingsHtml(html: str) -> str:
        html = html.replace("%anzeigezeit_Hersteller_value%", str(settings.SHOW_PRODUCER_INFOS_TIME))
        html = html.replace("%anzeigezeit_value%", str(settings.SHOW_TIME))
        html = html.replace("%changeAdvertiseTime_value%", str(settings.CHANGE_ADVERTISE_TIME))

        for i in range(1, 5):
            html = html.replace("%STATUS" + str(i) + "%", "")
        return html

    # Write Funktion in eigenem try-catch statement, um Html-Fehler senden zu können, wenn im SQL Teil
    # etwas fehlschlägt!
    def tryWriteOK(self, w_bytes: bytes) -> bool:
        try:
            self.wfile.write(w_bytes)
            return True
        except Exception as exc:
            log.warning("> Es ist ein Fehler im RequestHandler aufgetreten: write() failed: {0}".format(exc))
            return False

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        html_string: str = ""
        html_status: int = 200

        self.loc_db_mngr = localdatabasemanager.LocalDataBaseManager()
        self.loc_db_mngr.connect(settings.local_db_path)

        try:
            if self.path == "/log.html":
                log.debug("> Try to clear log...")

                if "password=" + settings.clear_log_file_pw + "&" in str(post_data):
                    if settings.log_file_delete_mode == "RENAME":
                        shutil.copyfile(settings.log_file_path, settings.log_file_path.replace(".log", "") + "_backup_"
                                        + datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ".log")

                        fo = open(settings.log_file_path, "w")
                        fo.truncate()
                        fo.close()

                        log.info("    -> Log renamed")

                        self.do_GET()
                        return
                    elif settings.log_file_delete_mode == "DELETE":
                        fo = open(settings.log_file_path, "w")
                        fo.truncate()
                        fo.close()

                        log.info("    -> Log deleted")

                        self.do_GET()
                        return
                    else:
                        log.error("   -> Fehler: Unbekannter log_file_delete_mode: {0}"
                                  .format(settings.log_file_delete_mode))
                        self.do_GET()
                        return
                else:
                    log.warning("   -> Clear/Delete failed: Wrong password: ".format(str(post_data)))
                    html_string = open("../html/tabelle-falsches-pw.html", "r").read()

            elif self.path == "/settings.html":
                if "ReloadAdvertiseListButton=TRUE" in str(post_data) \
                        or ("ReloadAdvertiseListButton.x" in
                            str(post_data) and "ReloadAdvertiseListButton.y" in str(post_data)):
                    settings.want_reload_advertise = True
                    log.info("> Reload Advertise List")
                    self.do_GET()
                    return
                else:
                    data = re.split('&|='.encode(), post_data)
                    admin: bool = False

                    if "adminPW".encode() in data and data.index("adminPW".encode()) < (len(data) - 1):
                        if data[data.index("adminPW".encode()) + 1].decode() == settings.clear_log_file_pw:
                            admin = True
                        else:
                            log.warning(" > Falsches Passwort in Webeinstellungen: {0}".
                                        format(data[data.index("adminPW".encode()) + 1].decode()))
                    else:
                        log.error(" > Kein Passwort in Webeinstellungen Postanfrage!.")

                    for i in range(0, len(data), 2):

                        if i == len(data) - 1 or data[i].decode() == "adminPW":
                            continue

                        elif data[i].decode() == "anzeigezeit_value":
                            # post_data.startswith("anzeigezeit_value=".encode("utf-8"))
                            html_string = open("../html/settings.html", "r").read()

                            if not admin:
                                html_string = html_string.replace("%anzeigezeit_value%", str(settings.SHOW_TIME))
                                html_string = html_string.replace("%STATUS1%",
                                                                  "<font color='red'>Aktualisierung fehlgeschlagen! "
                                                                  "Falsches Admin Passwort</font>")
                            elif data[i + 1].isdigit():
                                time = int(data[i + 1])
                                self.loc_db_mngr.setDelayTime("ARTIKEL", time)
                                settings.SHOW_TIME = time
                                html_string = html_string.replace("%anzeigezeit_value%", str(settings.SHOW_TIME))
                                html_string = html_string.replace("%STATUS1%",
                                                                  "<font color='green'>Erfolgreich aktualisiert!</font>"
                                                                  "")
                                log.info("> Aktualisiere Artikel Information Anzeigezeit zu: {0} Sekunden.".
                                         format(settings.SHOW_TIME))

                            else:
                                html_string = html_string.replace("%anzeigezeit_value%", str(settings.SHOW_TIME))
                                html_string = html_string.replace("%STATUS1%",
                                                                  "<font color='red'>Aktualisierung fehlgeschlagen! "
                                                                  "Keine Zahl?</font>")
                            html_string = self.replaceVarsInSettingsHtml(html_string)

                        elif data[i].decode() == "anzeigezeit_Hersteller_value":
                            # post_data.startswith("anzeigezeit_Hersteller_value=".encode("utf-8")):
                            html_string = open("../html/settings.html", "r").read()

                            if not admin:
                                html_string = html_string.replace("%anzeigezeit_Hersteller_value%",
                                                                  str(settings.SHOW_TIME))
                                html_string = html_string.replace("%STATUS2%",
                                                                  "<font color='red'>Aktualisierung fehlgeschlagen! "
                                                                  "Falsches Admin Passwort</font>")
                            elif data[i + 1].isdigit():
                                time = int(data[i + 1])
                                self.loc_db_mngr.setDelayTime("HERSTELLER", time)
                                settings.SHOW_PRODUCER_INFOS_TIME = time
                                html_string = html_string.replace("%anzeigezeit_Hersteller_value%",
                                                                  str(settings.SHOW_PRODUCER_INFOS_TIME))
                                html_string = html_string.replace("%STATUS2%",
                                                                  "<font color='green'>Erfolgreich aktualisiert!</font>"
                                                                  "")
                                log.info("> Aktualisiere Hersteller Informationen Anzeigezeit zu: {0} Sekunden.".
                                         format(settings.SHOW_PRODUCER_INFOS_TIME))
                            else:
                                html_string = html_string.replace("%anzeigezeit_Hersteller_value%",
                                                                  str(settings.SHOW_PRODUCER_INFOS_TIME))
                                html_string = html_string.replace("%STATUS2%",
                                                                  "<font color='red'>Aktualisierung fehlgeschlagen! "
                                                                  "Keine Zahl?</font>")
                            html_string = self.replaceVarsInSettingsHtml(html_string)

                        elif data[i].decode() == "changeAdvertiseTime_value":
                            # post_data.startswith("changeAdvertiseTime_value=".encode("utf-8")):
                            html_string = open("../html/settings.html", "r").read()

                            if not admin:
                                html_string = html_string.replace("%anzeigezeit_Hersteller_value%",
                                                                  str(settings.SHOW_TIME))
                                html_string = html_string.replace("%STATUS3%",
                                                                  "<font color='red'>Aktualisierung fehlgeschlagen! "
                                                                  "Falsches Admin Passwort</font>")
                            elif data[i + 1].isdigit():
                                time = int(data[i + 1])
                                self.loc_db_mngr.setDelayTime("CHANGE_ADVERTISE", time)
                                settings.CHANGE_ADVERTISE_TIME = time
                                print(time)
                                html_string = html_string.replace("%anzeigezeit_Hersteller_value%",
                                                                  str(settings.CHANGE_ADVERTISE_TIME))
                                html_string = html_string.replace("%STATUS3%",
                                                                  "<font color='green'>Erfolgreich aktualisiert!</font>"
                                                                  "")
                                log.info(
                                    "> Aktualisiere Wechselzeit zwischen Startseite und Werbung Seite zu: {0} Sekunden.".
                                    format(settings.CHANGE_ADVERTISE_TIME))
                            else:
                                html_string = html_string.replace("%anzeigezeit_Hersteller_value%",
                                                                  str(settings.CHANGE_ADVERTISE_TIME))
                                html_string = html_string.replace("%STATUS3%",
                                                                  "<font color='red'>Aktualisierung fehlgeschlagen! "
                                                                  "Keine Zahl?</font>")
                            html_string = self.replaceVarsInSettingsHtml(html_string)

                        elif data[i].decode() == "changePasswordNewPW_value":
                            # post_data.startswith("changeAdvertiseTime_value=".encode("utf-8")):
                            html_string = open("../html/settings.html", "r").read()

                            if not admin:
                                html_string = html_string.replace("%STATUS4%",
                                                                  "<font color='red'>Aktualisierung fehlgeschlagen! "
                                                                  "Falsches Admin Passwort</font>")
                            else:
                                self.loc_db_mngr.setPassword("ADMIN", data[i + 1].decode())
                                settings.clear_log_file_pw = data[i + 1].decode()

                                html_string = html_string.replace("%STATUS4%",
                                                                  "<font color='green'>Erfolgreich aktualisiert!</font>"
                                                                  "")
                                log.info("> Ändere das Admin Passwort")
                            html_string = self.replaceVarsInSettingsHtml(html_string)
                        else:
                            log.warning("> Unbekannter POST: {0}".format(str(post_data)))
                            html_string = open("../html/404.html", "r").read()
                            html_status = 404

            else:
                log.debug("> WARNUNG: Post Seite nicht gefunden: {0}".format(self.path))

                html_string = open("../html/404.html", "r").read()
                html_status = 404

            if html_string == "":
                log.warning("> Unbearbeiteter POST: {0}".format(str(post_data)))
                html_string = open("../html/404.html", "r").read()
                html_status = 404

            self.send_response(html_status)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()

            if not self.tryWriteOK(html_string.encode("utf-8")):
                self.loc_db_mngr = None
                return

        except Exception as exc:
            log.error("> Es ist ein Fehler im RequestHandler aufgetreten: {0}".format(exc))
            self.send_response(500)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.tryWriteOK("<h1>Ein unerwartetes Problem ist aufgetreten!</h1>".encode("utf-8"))
