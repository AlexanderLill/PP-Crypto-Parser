import unittest
from src.i18n.i18n import I18n

class I18nTest(unittest.TestCase):
    """Test case implementation for I18n"""

    def test_load_label(self):
        i18n = I18n("de")
        self.assertEquals(i18n.get("account.BUY"), "Kauf")

    def test_german_csv_headers_depot(self):
        i18n = I18n("de")
        self.assertEquals(";".join(i18n.get("DEPOT_COLUMNS")), "Datum;Uhrzeit;Typ;Wertpapier;Stück;Kurs;Betrag;Gebühren;Steuern;Gesamtpreis;Konto;Gegenkonto;Notiz;Quelle")
    
    def test_german_csv_headers_account(self):
        i18n = I18n("de")
        self.assertEquals(";".join(i18n.get("ACCOUNT_COLUMNS")), "Datum;Uhrzeit;Typ;Betrag;Saldo;Wertpapier;Stück;pro Aktie;Gegenkonto;Notiz;Quelle")
