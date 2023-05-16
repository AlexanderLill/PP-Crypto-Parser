# -*- coding: utf-8 -*-
"""
Transaction classes

Copyright 2022-05-16 AlexanderLill
"""
import json
import numbers
import locale
locale.setlocale(locale.LC_ALL, "de_DE.utf-8")  # TODO: Cleanup locale stuff

CSV_SEP = ";"

class DepotTransaction:
    """
    Datum;Typ;Wertpapier;Stück;Kurs;Betrag;Gebühren;Steuern;Gesamtpreis;Konto;Gegenkonto;Notiz;Quelle
    """
    def __init__(self, date, time, type, asset="", amount="", rate="", value="", fees="", taxes="", total="", account="", other_account="", note="", source=""):
        self.date = date
        self.time = time
        self.type = type
        self.asset = asset
        self.amount = amount
        self.rate = rate
        self.value = value
        self.fees = fees
        self.taxes = taxes
        self.total = total
        self.account = account
        self.other_account = other_account
        self.note = note
        self.source = source
    
    def __str__(self):
        return json.dumps(self, indent=4, sort_keys=True)
    
    def to_csv(self):
        result = ""
        result += f"{self.date}{CSV_SEP}"
        result += f"{self.time}{CSV_SEP}"
        result += f"{self.type}{CSV_SEP}"
        result += f"{self.asset}{CSV_SEP}"
        result += f"{locale.format_string('%.6f', self.amount, grouping=True, monetary=True) if isinstance(self.amount, numbers.Number) else self.amount}{CSV_SEP}"
        result += f"{locale.format_string('%.6f', self.rate, grouping=True, monetary=True) if isinstance(self.rate, numbers.Number) else self.rate}{CSV_SEP}"
        result += f"{locale.format_string('%.6f', self.value, grouping=True, monetary=True) if isinstance(self.value, numbers.Number) else self.value}{CSV_SEP}"
        result += f"{locale.format_string('%.6f', self.fees, grouping=True, monetary=True) if isinstance(self.fees, numbers.Number) else self.fees}{CSV_SEP}"
        result += f"{self.taxes}{CSV_SEP}"
        result += f"{locale.format_string('%.6f', self.total, grouping=True, monetary=True) if isinstance(self.total, numbers.Number) else self.total}{CSV_SEP}"
        result += f"{self.account}{CSV_SEP}"
        result += f"{self.other_account}{CSV_SEP}"
        result += f"{self.note}{CSV_SEP}"
        result += f"{self.source}"
        return result

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=True)


class AccountTransaction:
    """
    Datum;Typ;Betrag;Saldo;Wertpapier;Stück;pro Aktie;Gegenkonto;Notiz;Quelle
    """
    def __init__(self, date, time, type, amount, value="", asset="", pieces="", per_piece="", account="", note="", source=""):
        self.date = date
        self.time = time
        self.type = type
        self.amount = amount
        self.value = value
        self.asset = asset
        self.pieces = pieces
        self.per_piece = per_piece
        self.account = account
        self.note = note
        self.source = source
    
    def __str__(self):
        return json.dumps(self, indent=4, sort_keys=True)
    
    def to_csv(self):
        result = ""
        result += f"{self.date}{CSV_SEP}"
        result += f"{self.time}{CSV_SEP}"
        result += f"{self.type}{CSV_SEP}"
        result += f"{locale.format_string('%.6f', self.amount, grouping=True,monetary=True) if isinstance(self.amount, numbers.Number) else self.amount}{CSV_SEP}"
        result += f"{self.value}{CSV_SEP}"
        result += f"{self.asset}{CSV_SEP}"
        result += f"{self.pieces}{CSV_SEP}"
        result += f"{self.per_piece}{CSV_SEP}"
        result += f"{self.account}{CSV_SEP}"
        result += f"{self.note}{CSV_SEP}"
        result += f"{self.source}"
        return result

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=True)