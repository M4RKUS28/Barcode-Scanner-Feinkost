# Barcode-Scanner-Feinkost-

Mit diesem Programm sollen Kunden durch das Scannen eines Produkt Bar Codes zusätzliche Informationen zu diesem bekommen.

# Autostart mit Cronjobs:
Grundsätzlich gibt es für den Autostart (hier angeführt) zwei Möglichkeiten zur Umsetzung in Linux. Die erste ist der Autostart mit Cronjobs.
Für die erste muss das Paket cron installiert werden:

``sudo apt install cron``

Als nächstes kann man das Programm der Autostartliste mit: ``crontab -e`` hinzufügen:
````
@reboot python3.7 /path/to/the/project/main.py
````

# Autostart mit Systemd:
Die andere Möglichkeit funktioniert nur auf Systemd basierenden Systemen, bietet aber zudem die Möglichkeit,
das Programm erst nach der Netzwerkverbindung zu starten, die für die DB Anbindung vonnöten ist.

Dazu muss man die Datei ``/etc/systemd/system/feinkostBarcodeScanner.service`` mit dem Text erstellen:
````
[Unit]
Description=Feinkost Barcode Scanner
After=network.target

[Service]
Type=oneshot
ExecStart=/full/path/to/the/project/main.py
User=pi

[Install]
WantedBy=multi-user.target

````

``User=pi`` muss dabei noch zu dem Benutzer, der das Programm ausführt, geändert werden,
und sollte kein sudo Benutzer sein.
``ExecStart=/full/path/to/the/project/main.py`` zu dem Programmpfad.


Aktiviert wird der Autostart durch den Befehl:
``sudo systemctl daemon-reload`` und
``sudo systemctl enable feinkostBarcodeScanner``,\
deaktiviert mit: ``sudo systemctl disable feinkostBarcodeScanner``

# Abhängigkeiten Installation zusammengefasst:
Durch folgenden Bash-Code sollten alle benötigten Abhängigkeiten installiert werden. Sollten dabei Probleme auftreten,
werden darauffolgend noch einmal alle Schritte detaillierter aufgeführt.

````
# 1. Driver
sudo apt install tdsodbc freetds-dev freetds-bin unixodbc-dev

# Save driver Location for Driver Loader
sudo tee -a "/etc/odbcinst.ini" "[FreeTDS]
Description=FreeTDS Driver
Driver=/usr/lib/arm-linux-gnueabihf/odbc/libtdsodbc.so
Setup=/usr/lib/arm-linux-gnueabihf/odbc/libtdsS.so"

# 2. Driver Loader, 3. Graphics, 4. Python-modules:
sudo apt install python3-pyodbc python3-PySide2.* python-enum34
````


# Dependencies installieren:
Da es viele Pakete nur in älteren Version gibt, wird Python 3.7 empfohlen


## 1. MS SQL Open Source Driver:

``sudo apt install tdsodbc freetds-dev freetds-bin unixodbc-dev``

Getestet mit: \
tdsodbc/oldstable,now 1.00.104-1+deb10u1 armhf \
ODBC driver for connecting to MS SQL and Sybase SQL servers 

### Einrichten des Drivers nach der Installation:
[Connect to MSSQL using FreeTDS / ODBC in Python. - Github](https://gist.github.com/rduplain/1293636#file-readme-md) \
[What's causing 'unable to connect to data source' for pyodbc? - Stackoverflow](https://stackoverflow.com/questions/9723656/whats-causing-unable-to-connect-to-data-source-for-pyodbc)

Mit `` sudo nano /etc/odbcinst.ini`` folgenden Text einfügen:

einfügen und ggf. Pfade ändern (manchmal auch unter /usr/lib/odbc/):
````
[FreeTDS]
Description=FreeTDS Driver
Driver=/usr/lib/arm-linux-gnueabihf/odbc/libtdsodbc.so
Setup=/usr/lib/arm-linux-gnueabihf/odbc/libtdsS.so
````

Dadurch kann pyodbc den Driver finden. Weitere Informationen unter \
[FreeTDS.support.Microsoft](https://www.freetds.org/faq.html#Does.FreeTDS.support.Microsoft.servers) \
bzw. Informationen zur Protokollversion unter \
[ChoosingTdsProtocol](https://www.freetds.org/userguide/ChoosingTdsProtocol.html)


## Oder Driver offiziell von Mircosoft
(Kein Support für ArmV8-Architektur! -> Funktioniert nicht auf dem Raspberry-Pi)

[Microsoft Download Seite zu odbc-driver-for-sql](https://docs.microsoft.com/de-de/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16)

## 2. Zum Laden des Datenbank Drivers pyodbc:

``sudo apt install python3-pyodbc``

Getestet mit: \
python3-pyodbc/oldstable,now 4.0.22-1+b1 armhf \
Python3 module for ODBC database access 


## 3. Für die Grafik: PyQt bzw. hier Pyside2 Bibliotheken:

``sudo apt install python3-PySide2.*``

## 4. Weitere benötigte Python Module:
``sudo apt install python-enum34``



