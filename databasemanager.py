import pyodbc


class DataBaseManager:
    cnxn = None

    def __init__(self):
        # cnxn = pyodbc.connect("DRIVER={ODBC Driver 18 for SQL Server};"
        #                      "Server=PC-MARKUS;"
        #                      "Database=PC-MARKUS;"
        #                      "Trusted_Connection=yes;"
        #                      "uid=test;pwd=altinsystems;")
        return

    def connect(self, ip="PC-MARKUS", port=None, user="test", pw="altinsystems", db="Mandant_1"):
        self.cnxn = pyodbc.connect(driver='{ODBC Driver 18 for SQL Server}', host=ip, database=db,
                                   trusted_connection="yes", user=user, password=pw, encrypt="no")
        return

    def get_header_list(self):
        if self.cnxn is None:
            print("ERROR: Not Connected!")
            return None

        try:
            cursor = self.cnxn.cursor()
            cursor.execute('SELECT * FROM ArtikelVerwaltung.vArtikelliste')

            columns = [column[0] for column in cursor.description]
            return columns
        except Exception as exc:
            print('critical error occurred: {0}. Please save your data and restart application'.format(exc))
            return None

    def get_data_by_ean(self, ean):
        if self.cnxn is None:
            print("ERROR: Not Connected!")
            return None

        try:
            cursor = self.cnxn.cursor()
            cursor.execute("SELECT * FROM ArtikelVerwaltung.vArtikelliste WHERE vArtikelliste.EAN = ?", ean)
            row = cursor.fetchone()
            if row is None or len(cursor.fetchall()) != 0:
                print("Error: Keinen oder mehrere Einträge gefunden!")
            return row

        except Exception as exc:
            print('critical error occurred: {0}. Please save your data and restart application'.format(exc))
            return None

    def p_all(self):
        cursor = self.cnxn.cursor()
        cursor.execute('SELECT * FROM ArtikelVerwaltung.vArtikelliste')
        columns = [column[0] for column in cursor.description]
        for column in columns:
            print(column)
        for row in cursor:
            print('row = %r' % (row,))
    
    def get_image_list(self):
        if self.cnxn is None:
            print("ERROR: Not Connected!")
            return None

        try:
            cursor = self.cnxn.cursor()
            cursor.execute( "SELECT  DISTINCT  dbo.tBild.kBild, dbo.tArtikel.kArtikel   FROM dbo.tBild, dbo.tArtikel, dbo.tArtikelbildPlattform "
                           "WHERE dbo.tArtikel.kArtikel = ( SELECT dbo.tArtikelbildPlattform.kArtikel FROM dbo.tArtikelbildPlattform "
                                "WHERE dbo.tArtikelbildPlattform.kBild = dbo.tBild.kBild AND  dbo.tArtikelbildPlattform.kPlattform = 1 )" )
            return cursor.fetchall()

        except Exception as exc:
            print('critical error occurred: {0}. Please save your data and restart application'.format(exc))
            return None


# kArtikel kStueckliste kVaterArtikel kArtikelForKategorieArtikel Artikelnummer Sortiernummer Artikelname Einheit EAN
# Herkunftsland UNNUmmer cHAN Gefahrennummer ISBN ASIN TaricCode UPC Hersteller Lieferstatus Breite Hoehe Laenge
# Erstelldatum
