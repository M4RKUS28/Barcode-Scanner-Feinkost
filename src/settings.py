
####
# Einstellungen
####

# Programm Version
PROGRAMM_VERSION: str = "0.9.6"


####
# MS SQL Server
####

SQL_DRIVER_USED_VERSION_MS_DRIVER: str = "{ODBC Driver 18 for SQL Server}"
SQL_DRIVER_USED_VERSION_FreeTDS: str = "{FreeTDS}"
SQL_DRIVER_USED_VERSION_FreeTDS_VERSION: str = "7.4"

# MS SQL Server mit Daten zu Produkten
ms_sql_server_ip: str = "home.obermui.de"
# MS SQL Server Port
ms_sql_server_port: int = 18769

# Merkmal MetaLine aktive value
wawi_advertise_aktive_meta_keyword: str = 'ANZEIGEN=TRUE'

want_reload_advertise: bool = False

####
# SQL Lite Datenbank
####

# Pfad zu lokaler Datenbank, die zum Speichern der Statistiken der Nutzung, sowie der Bewertung dient
local_db_path: str = "./sqlLiteDB.db"


####
# HTTP Server
####

# Lokaler HTTP SERVER LISTEN IP
local_http_server_ip: str = "0.0.0.0"
# Lokaler HTTP SERVER LISTEN Port
local_http_server_port: int = 8888
# Passwort zum Leeren des Logfiles
clear_log_file_pw: str = "pass"
# Anzahl der Elemente auf einer Internetseite beim Webserver
item_count_on_web_server_list: int = 100
# rename or delete logFile: ( RENAME | DELETE ):
log_file_delete_mode: str = "RENAME"


####
# Logging
####

# Pfad zur Logdatei
log_file_path: str = './../Dokumentation/feinkostBarcodeScannerLog.log'


####
# GUI
####

# Pfad zu Qt-Designer Formulardatei: Die Grafik wurde nämlich mithilfe des Qt Creators erstellt.
ui_file_path: str = "../src/form_ALT.ui"

# Dauer der Zeit, wie lange die Information zu einem Produkt angezeigt werden, in Sekunden
SHOW_TIME: int = 15
# auer der Zeit, wie lange "Keine Informationen zu diesem Produkt gefunden" angezeigt wird, in Sekunden
SHOW_TIME_NOTHING_FOUND: int = 8
# Dauer der Zeit zwischen einem Wechsel der Warte-Anzeige in Sekunden
CHANGE_ADVERTISE_TIME: int = 15
# Dauer der Zeit, wie lange die Information zum Hersteller angezeigt werden, in Sekunden
SHOW_PRODUCER_INFOS_TIME: int = 20

# Höhe des roten Balkens, der den normalen Preis durchstreicht (für Sonderpreis) in Pixel
SPECIAL_PRICE_RED_LINE_HEIGHT: int = 5
# Abstand zwischen normalen Preis und Sonderpreis in Pixel
SPACE_BETWEEN_PRICE_AND_SPECIAL_PRICE: int = 10
# Schriftgröße des Sonderpreises
SPECIAL_PRICE_FONT_SIZE: int = 18

