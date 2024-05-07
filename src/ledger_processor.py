# -*- coding: utf-8 -*-
"""
LedgerProcessor module

Copyright 2022-05-16 AlexanderLill
"""
from src.transactions import DepotTransaction, AccountTransaction
from .i18n import I18n

import json
import numbers
import pandas as pd

class IllegalArgumentError(ValueError):
    pass

class LedgerProcessor:

    ACCOUNT_TRANSACTIONS = "account_transactions"
    DEPOT_NORMAL_TRANSACTIONS = "depot_normal_transactions"
    DEPOT_SPECIAL_TRANSACTIONS = "depot_special_transactions"

    def __init__(self, filename=None, csv_sep=",", dataframe=None,
                 fiat_currency="EUR", rate_provider=None, refids_to_ignore="",
                 depot_current="", depot_new="", account="", language="de"):

        if dataframe is None:
            if filename is None:
                raise IllegalArgumentError("Either filename or dataframe needs to be specified!")
            dataframe = pd.read_csv(filename, sep=csv_sep)
        
        self._i18n = I18n(language)
        # shortcuts for i18n values
        self.DELIVERY_INBOUND = self._i18n.get("portfolio.DELIVERY_INBOUND")
        self.BUY = self._i18n.get("account.BUY")
        self.SELL = self._i18n.get("account.SELL")
        self.FEES = self._i18n.get("account.FEES")

        self._depot_csv_header = ";".join(self._i18n.get("DEPOT_COLUMNS"))
        self._account_csv_header = ";".join(self._i18n.get("ACCOUNT_COLUMNS"))

        self._df = dataframe
        self._fiat_currency = fiat_currency
        self._rate_provider = rate_provider
        
        self.depot_current = depot_current
        self.depot_new = depot_new
        self.account = account

        refids_to_ignore = refids_to_ignore.split(",")
        refids_to_ignore = filter(lambda id: len(id)>0, refids_to_ignore)
        self._refids_to_ignore = list(refids_to_ignore)

        self._process_transactions()

    def __create_dateandtime(row):
        row["Date"] = row["time"].split()[0]
        row["Time"] = row["time"].split()[1].split(".")[0]
        return row
    
    def __get_abs_amount(self, orig_amount):
        if not isinstance(orig_amount, numbers.Number):
            return orig_amount
        else:
            amount = float(orig_amount)
            if amount < 0:
                return amount * -1.0
            else:
                return amount
    
    def __get_abs_amount_with_sign(self, orig_amount):
        if not isinstance(orig_amount, numbers.Number):
            return orig_amount
        else:
            amount = float(orig_amount)
            if amount < 0:
                return amount * -1.0, -1
            else:
                return amount, 1

    def _get_ids_summary(self, transactions):
        ids = {}
        for idt in ["refid", "txid"]:
            ids[idt] = []
            for t in transactions:
                if idt in t and len(t[idt]) > 0:
                    ids[idt].append(t[idt])
            ids[idt] = list(set(ids[idt]))

        result = ",".join(sorted(ids["refid"]))
        if len(ids["txid"]) > 0:
            result += "," + ",".join(sorted(ids["txid"]))
        return result

    def _generate_csv_from(self, transactions):
        result_csv = "\n"
        for t in transactions:
            result_csv = result_csv + t.to_csv() + "\n"
        return result_csv

    def store_depot_normal_transactions(self, output_filename):
        transactions = self.get_transactions().get(self.DEPOT_NORMAL_TRANSACTIONS, [])
        csv_output = self._depot_csv_header + self._generate_csv_from(transactions)

        with open(output_filename, "w") as file:
            file.write(csv_output)
    
    def store_depot_special_transactions(self, output_filename):
        transactions = self.get_transactions().get(self.DEPOT_SPECIAL_TRANSACTIONS, [])
        csv_output = self._depot_csv_header + self._generate_csv_from(transactions)

        # This is necessary as inbound deliveries are not supported by PP CSV Import
        # During the import in PP check the box to transform buys into inbound deliveries (see README.md)
        csv_output = csv_output.replace(
            f";{self.DELIVERY_INBOUND};",
            f";{self.BUY};"
        )

        with open(output_filename, "w") as file:
            file.write(csv_output)
    
    def store_account_transactions(self, output_filename):
        transactions = self.get_transactions().get(self.ACCOUNT_TRANSACTIONS, [])
        csv_output = self._account_csv_header + self._generate_csv_from(transactions)

        with open(output_filename, "w") as file:
            file.write(csv_output)
    
    def _process_fiat_deposit(self, transaction_id, transaction):
        raw_transactions = list(sorted(transaction["raw"], key=lambda item: item["time"], reverse=True))

        """
        {
            "Date": "2021-04-21",
            "Time": "07:03:52",
            "WKN": "ZEUR",
            "aclass": "currency",
            "amount": 1000.0,
            "asset": "ZEUR",
            "balance": NaN,
            "fee": 0.0,
            "refid": "QCCJ7TH-6AV55J-YXZMBA",
            "subtype": NaN,
            "time": "2021-04-21 07:03:52",
            "txid": NaN,
            "type": "deposit"
        },
        {
            "Date": "2021-04-21",
            "Time": "07:04:27",
            "WKN": "ZEUR",
            "aclass": "currency",
            "amount": 1000.0,
            "asset": "ZEUR",
            "balance": 1000.0075,
            "fee": 0.0,
            "refid": "QCCJ7TH-6AV55J-YXZMBA",
            "subtype": NaN,
            "time": "2021-04-21 07:04:27",
            "txid": "LYDWIG-T7LFD-BYIFHU",
            "type": "deposit"
        }
        """

        note_ids = self._get_ids_summary(raw_transactions)

        lt = raw_transactions[0]

        at = AccountTransaction(lt["Date"], lt["Time"], self._i18n.get("account.DEPOSIT"), lt["amount"], note=note_ids)

        return [at], []
    
    def _process_crypto_deposit(self, transaction_id, transaction):
        raw_transactions = list(sorted(transaction["raw"], key=lambda item: item["time"], reverse=True))

        """
        {
            "Date": "2020-12-27",
            "Time": "10:49:55",
            "WKN": "BCH",
            "aclass": "currency",
            "amount": 0.04564996,
            "asset": "BCH",
            "balance": NaN,
            "fee": 0.0,
            "refid": "QGEAOWO-KDDLPS-SEZYR4",
            "subtype": NaN,
            "time": "2020-12-27 10:49:55",
            "txid": NaN,
            "type": "deposit"
        },
        {
            "Date": "2020-12-27",
            "Time": "14:20:35",
            "WKN": "BCH",
            "aclass": "currency",
            "amount": 0.04564996,
            "asset": "BCH",
            "balance": 0.04564996,
            "fee": 0.0,
            "refid": "QGEAOWO-KDDLPS-SEZYR4",
            "subtype": NaN,
            "time": "2020-12-27 14:20:35",
            "txid": "LI23O6-3HOWX-H7ABRD",
            "type": "deposit"
        }
        """

        note_ids = self._get_ids_summary(raw_transactions)

        lt = raw_transactions[0]

        date_time = lt["time"]
        date = lt["Date"]
        time = lt["Time"]
        amount = lt["amount"]
        asset_normalized = self.__normalize_currency_abbreviation(lt["asset"])

        rate = "DUMMYRATE"
        value = "DUMMYVAL"
        total = "DUMMYTOTAL"
        if self._rate_provider:
            rate = self._rate_provider.get_rate(asset_normalized, date_time)
            value = round(amount * rate, 8)
            total = value

        dt = DepotTransaction(date,
                              time,
                              self.DELIVERY_INBOUND,
                              asset_normalized,
                              lt["amount"],
                              rate,
                              value,
                              "",
                              "",
                              total,
                              self.depot_current,
                              "",
                              note_ids
                             )

        return [], [dt]
    
    def _process_deposit(self, transaction_id, transaction):
        raw_transactions = list(sorted(transaction["raw"], key=lambda item: item["time"], reverse=True))

        currencies = set([t["asset"] for t in raw_transactions])
        if len(currencies) == 1 and self.__currency_is_in_set(currencies, self._fiat_currency):
            ats, dts = self._process_fiat_deposit(transaction_id, transaction)
        else:
            ats, dts = self._process_crypto_deposit(transaction_id, transaction)

        return ats, dts

    def __normalize_currency_abbreviation(self, crypto_currency):
        if crypto_currency[0] == 'Z' or crypto_currency[0] == 'X':
            return crypto_currency[1:]
        elif "." in crypto_currency:
            return crypto_currency.split(".")[0]
        else:
            return crypto_currency
    
    def __are_same_currency(self, observed_currency, expected_currency):
        if expected_currency in observed_currency:
            return True
        return False
    
    def __currency_is_in_set(self, currency_set, expected_currency):
        for currency in list(currency_set):
            if expected_currency in currency:
                return True
        return False

    def _process_trade(self, transaction_id, transaction):
        raw_transactions = list(sorted(transaction["raw"], key=lambda item: item["time"], reverse=True))

        tfiat_transactions = list(filter(lambda t: self.__are_same_currency(t["asset"], self._fiat_currency), raw_transactions))
        tcrypto_transactions = list(filter(lambda t: not self.__are_same_currency(t["asset"], self._fiat_currency), raw_transactions))

        if len(tfiat_transactions) != 1 or len(tcrypto_transactions) != 1:
            self.__print_transaction_debug_info("Trade does not consist of 1 fiat and 1 crypto transaction, skipping...", transaction)
            return [], []

        tfiat = tfiat_transactions[0]
        tcrypto = tcrypto_transactions[0]

        """
        {
            "Date": "2022-02-24",
            "Time": "08:57:02",
            "WKN": "ZEUR",
            "aclass": "currency",
            "amount": -1499.9999,
            "asset": "ZEUR",
            "balance": 793.5752,
            "fee": 2.4,
            "refid": "TTWFFE-HZX34-2EEGRM",
            "subtype": NaN,
            "time": "2022-02-24 08:57:02",
            "txid": "LU4MDZ-PSSAV-7KKYF2",
            "type": "trade"
        },
        {
            "Date": "2022-02-24",
            "Time": "08:57:02",
            "WKN": "XXBT",
            "aclass": "currency",
            "amount": 0.04746069,
            "asset": "XXBT",
            "balance": 0.0474667,
            "fee": 0.0,
            "refid": "TTWFFE-HZX34-2EEGRM",
            "subtype": NaN,
            "time": "2022-02-24 08:57:02",
            "txid": "L3H4BL-PFLZU-JVX2JY",
            "type": "trade"
        }
        """

        note_ids = self._get_ids_summary(raw_transactions)
        crypto_currency = self.__normalize_currency_abbreviation(tcrypto["asset"])

        date = tcrypto["Date"]
        time = tcrypto["Time"]

        fiat_amount, fiat_sign = self.__get_abs_amount_with_sign(tfiat["amount"])
        is_buy_transaction = True if fiat_sign < 0 else False
        crypto_amount = self.__get_abs_amount(tcrypto["amount"])

        rate = fiat_amount / crypto_amount

        fee_fiat = ""
        if isinstance(tfiat["fee"], numbers.Number):
            if float(tfiat["fee"]) > 0:
                fee_fiat = tfiat["fee"]
        
        fee_crypto = ""
        if isinstance(tcrypto["fee"], numbers.Number):
            if float(tcrypto["fee"]) > 0:
                fee_crypto = tcrypto["fee"]
        
        if isinstance(fiat_amount, numbers.Number) and isinstance(fee_fiat, numbers.Number):
            if is_buy_transaction:
                total = fiat_amount + fee_fiat
            else:
                total = fiat_amount - fee_fiat
        elif isinstance(fiat_amount, numbers.Number):
            total = fiat_amount
        else:
            total = 0.0
        
        transaction_type = self.BUY if is_buy_transaction else self.SELL

        if fee_crypto != "":
            fee_value = round(fee_crypto * rate, 8)
        else:
            fee_value = ""
        
        depot_transactions = []
        account_transactions = []

        dt = DepotTransaction(date,
                              time,
                              transaction_type,
                              crypto_currency,
                              crypto_amount,
                              rate,
                              fiat_amount,
                              fee_fiat,
                              "",
                              total,
                              self.depot_current,
                              self.account,
                              note_ids
                             )
        
        depot_transactions.append(dt)
    
        # If there is a fee, we create a sell transaction, and a cost transaction with same amount.
        if fee_crypto != "":

            sellt = DepotTransaction(date,
                                    time,
                                    self.SELL,
                                    crypto_currency,
                                    fee_crypto,
                                    rate,
                                    fee_value,
                                    "",
                                    "",
                                    fee_value,
                                    self.depot_current,
                                    self.account,
                                    note_ids
                                )
        
            costt = AccountTransaction(date,
                                    time,
                                    self.FEES,
                                    fee_value,
                                    "",
                                    crypto_currency,
                                    "",
                                    "",
                                    "",
                                    note_ids
                                    )
            
            depot_transactions.append(sellt)
            account_transactions.append(costt)

        return account_transactions, depot_transactions
    
    def _process_withdrawal(self, transaction_id, transaction):
        raw_transactions = list(sorted(transaction["raw"], key=lambda item: item["time"], reverse=True))

        currencies = set([t["asset"] for t in raw_transactions])
        if self.__currency_is_in_set(currencies, self._fiat_currency):
            ats, dts = self._process_fiat_withdrawal(transaction_id, transaction)
        else:
            ats, dts = self._process_crypto_withdrawal(transaction_id, transaction)

        return ats, dts

    def _process_fiat_withdrawal(self, transaction_id, transaction):
        raw_transactions = list(sorted(transaction["raw"], key=lambda item: item["time"], reverse=True))

        """
        {
            'txid': 'LHXLZ6-GJHOM-LWBXPR'
            'refid': 'FTLn8NT-Nwp5SHbaVhOwuQeZXkeBBc'
            'time': '2024-01-26 22:35:17'
            'type': 'withdrawal'
            'subtype': ''
            'aclass': 'currency'
            'asset': 'ZEUR'
            'amount': -13.51
            'fee': 0.09
            'balance': 0.0014
            'Date': '2024-01-26'
            'Time': '22:35:17'
        }
        """

        note_ids = self._get_ids_summary(raw_transactions)

        lt = raw_transactions[0]

        abs_amount = self.__get_abs_amount(lt["amount"])

        withdrawal = AccountTransaction(lt["Date"], lt["Time"], self._i18n.get("account.REMOVAL"), abs_amount, "", "", "", "", "", note_ids)
        fees = AccountTransaction(lt["Date"], lt["Time"], self.FEES, float(lt["fee"]), "", "", "", "", "", note_ids)

        return [withdrawal, fees], []

    def _process_crypto_withdrawal(self, transacion_id, transaction):
        raw_transactions = list(sorted(transaction["raw"], key=lambda item: item["time"], reverse=True))

        """
        {
            "Date": "2021-11-03",
            "Time": "20:15:19",
            "WKN": "XXBT",
            "aclass": "currency",
            "amount": -0.03076,
            "asset": "XXBT",
            "balance": NaN,
            "fee": 0.00015,
            "refid": "AGB76R3-DWC5SC-UCBGGX",
            "subtype": NaN,
            "time": "2021-11-03 20:15:19",
            "txid": NaN,
            "type": "withdrawal"
        },
        {
            "Date": "2021-11-03",
            "Time": "21:02:37",
            "WKN": "XXBT",
            "aclass": "currency",
            "amount": -0.03076,
            "asset": "XXBT",
            "balance": 6.01e-06,
            "fee": 0.00015,
            "refid": "AGB76R3-DWC5SC-UCBGGX",
            "subtype": NaN,
            "time": "2021-11-03 21:02:37",
            "txid": "LU6WLT-MWUUY-BVWZ6E",
            "type": "withdrawal"
        }
        """

        lt = raw_transactions[0]

        date_time = lt["time"]
        date = lt["Date"]
        time = lt["Time"]
        transaction_amount = self.__get_abs_amount(lt["amount"])
        transaction_fee = self.__get_abs_amount(lt["fee"])
        asset_normalized = self.__normalize_currency_abbreviation(lt["asset"])

        rate = "DUMMYRATE"
        transaction_value = "DUMMYVAL"
        fee_value = "DUMMYFEES"
        transaction_total = "DUMMYTOTAL"
        fee_total = "DUMMYFEES"

        if self._rate_provider:
            rate = self._rate_provider.get_rate(asset_normalized, date_time)

            # Transfer
            transaction_value = round(transaction_amount * rate, 8)
            transaction_total = transaction_value

            # Fees
            fee_f = transaction_fee
            fee_value = round(fee_f * rate, 8)
            fee_total = fee_value

        note_ids = self._get_ids_summary(raw_transactions)

        transfert = DepotTransaction(date,
                                     time,
                                     self._i18n.get("account.TRANSFER_OUT"),
                                     asset_normalized,
                                     transaction_amount,
                                     rate,
                                     transaction_value,
                                     "",
                                     "",
                                     transaction_total,
                                     self.depot_current,
                                     self.depot_new,
                                     note_ids)
        
        sellt = DepotTransaction(date,
                                 time,
                                 self.SELL,
                                 asset_normalized,
                                 transaction_fee,
                                 rate,
                                 fee_value,
                                 "",
                                 "",
                                 fee_total,
                                 self.depot_current,
                                 self.account,
                                 note_ids
                                )
        
        costt = AccountTransaction(date,
                                   time,
                                   self.FEES,
                                   fee_total,
                                   "",
                                   asset_normalized,
                                   "",
                                   "",
                                   "",
                                   note_ids
                                  )

        return [costt], [transfert, sellt]
    
    def _process_staking(self, transaction_id, transaction):
        raw_transactions = list(sorted(transaction["raw"], key=lambda item: item["time"], reverse=True))

        """
        {
            "txid": "L4U7Y4-WP76L-34UMSV",
            "refid": "STFCFLD-65INO-G3O54V",
            "time": "2022-12-11 03:41:47",
            "type": "staking",
            "subtype": "",
            "aclass": "currency",
            "asset": "ATOM.S",
            "amount": 0.003443,
            "fee": 0.0,
            "balance": 2.099724,
            "Date": "2022-12-11",
            "Time": "03:41:47"
        },
        {
            "txid": "",
            "refid": "RUGLWVG-XQGB5M-MHHHL7",
            "time": "2022-12-11 01:03:09",
            "type": "deposit",
            "subtype": "",
            "aclass": "currency",
            "asset": "ATOM.S",
            "amount": 0.003443,
            "fee": 0.0,
            "balance": "",
            "Date": "2022-12-11",
            "Time": "01:03:09"
        }
        """

        lt = raw_transactions[0]

        asset_normalized = self.__normalize_currency_abbreviation(lt["asset"])

        date_time = lt["time"]
        date = lt["Date"]
        time = lt["Time"]
        amount = self.__get_abs_amount(lt["amount"])
        rate = "DUMMYRATE"
        value = "DUMMYVAL"
        total = "DUMMYTOTAL"

        if self._rate_provider:
            rate = self._rate_provider.get_rate(asset_normalized, date_time)

            value = round(amount * rate, 8)
            total = value

        note_ids = self._get_ids_summary(raw_transactions)

        dt = DepotTransaction(date,
                              time,
                              self.DELIVERY_INBOUND,
                              asset_normalized,
                              lt["amount"],
                              rate,
                              value,
                              "",
                              "",
                              total,
                              self.depot_current,
                              "",
                              note_ids
                             )

        return [], [dt]
    
    def __is_staking_transfer(self, transaction):
        for t in transaction.get("raw", []):
            subtype = t.get("subtype", "")
            if subtype == "spotfromfutures" or \
                subtype == "spottostaking" or \
                subtype == "stakingfromspot" or \
                subtype == "stakingtospot" or \
                subtype == "spotfromstaking":
                return True
        return False

    def __print_transaction_debug_info(self, message, transaction):
        print(message + ", detailed transaction:", json.dumps(transaction))

    def _process_transaction(self, transaction_id, transaction):
        parsing_info = transaction.get("meta", {}).get("parsing_info", "")
        transaction_types = set(transaction.get("types", []))

        if parsing_info in ["dup", "nondup"] and transaction_types == {"deposit"}:
            return self._process_deposit(transaction_id, transaction)
        elif parsing_info == "dup" and transaction_types == {"withdrawal"}:
            return self._process_withdrawal(transaction_id, transaction)
        elif parsing_info in ["dup", "nondup"] and transaction_types == {"trade"}:
            return self._process_trade(transaction_id, transaction)
        elif parsing_info == "dup" and transaction_types == {"spend","receive"}:
            return self._process_trade(transaction_id, transaction)
        elif parsing_info == "dup_asset_amount_match" and transaction_types == {"deposit","staking"}:
            return self._process_staking(transaction_id, transaction)
        elif parsing_info == "nondup" and transaction_types == {"staking"}:
            return self._process_staking(transaction_id, transaction)
        elif parsing_info == "nondup" and transaction_types == {"earn"}:
            return self._process_staking(transaction_id, transaction)
        elif parsing_info == "nondup" and transaction_types == {"transfer"}:
            if self.__is_staking_transfer(transaction):
                print(f"Ignoring staking transfer... ({parsing_info}, {transaction_types})")
                return [], []
            else:
                self.__print_transaction_debug_info(f"Can't process unknown case [NDT] ({parsing_info}, {transaction_types})", transaction)
                return [], []
        elif parsing_info == "dup" and transaction_types == {"transfer", "withdrawal"}:
            if self.__is_staking_transfer(transaction):
                print(f"Ignoring staking transfer... ({parsing_info}, {transaction_types})")
                return [], []
            else:
                self.__print_transaction_debug_info(f"Can't process unknown case [DTW-NS] ({parsing_info}, {transaction_types})", transaction)
                return [], []
        elif parsing_info == "dup" and transaction_types == {"deposit", "transfer"}:
            if self.__is_staking_transfer(transaction):
                print(f"Ignoring staking transfer... ({parsing_info}, {transaction_types})")
                return [], []
            else:
                self.__print_transaction_debug_info(f"Can't process unknown case [DDT-NS] ({parsing_info}, {transaction_types}): ", transaction)
                return [], []
        elif parsing_info == "nondup" and transaction_types == {"withdrawal"}:
            return self._process_fiat_withdrawal(transaction_id, transaction)
        else:
            if parsing_info == "dup_asset_amount_match":
                self.__print_transaction_debug_info(f"Can't process unknown case, but could be false positive [FP] ({parsing_info}, {transaction_types})", transaction)
                return [], []
            else:
                self.__print_transaction_debug_info(f"Can't process unknown case [ELSE] ({parsing_info}, {transaction_types})", transaction)
                return [], []
    
    def get_transactions(self):
        account_transactions = self.account_transactions
        depot_normal_transactions = list(filter(lambda t: t.type != self.DELIVERY_INBOUND, self.depot_transactions))
        depot_special_transactions = list(filter(lambda t: t.type == self.DELIVERY_INBOUND, self.depot_transactions))

        return {
            self.ACCOUNT_TRANSACTIONS: account_transactions,
            self.DEPOT_NORMAL_TRANSACTIONS: depot_normal_transactions,
            self.DEPOT_SPECIAL_TRANSACTIONS: depot_special_transactions,
        }
    
    def _process_transactions(self):
        transactions = self._parse_transactions()

        account_transactions = []
        depot_transactions = []

        for transaction_id, transaction in transactions.items():
            new_account_transactions, new_depot_transactions = self._process_transaction(transaction_id, transaction)
            account_transactions.extend(new_account_transactions)
            depot_transactions.extend(new_depot_transactions)
        
        self.account_transactions = account_transactions
        self.depot_transactions = depot_transactions

    def _parse_transactions(self):
        df = self._df
        df = df.fillna("")
        df = df.apply(LedgerProcessor.__create_dateandtime, axis=1)
        df = df.sort_values(['refid', 'time'], ascending = [True, True])

        raw_ledger = df.to_dict('records')    

        refid_dups = df.groupby('refid').count()
        refid_dups = refid_dups[refid_dups["txid"] > 1]
        refid_dups = list(refid_dups.index)

        transactions = {}

        # Process dups (transactions belonging together, eg buy consisting of spending EUR, getting crypto)

        dups_to_process = list(filter(lambda item: item["refid"] in refid_dups, raw_ledger))
        for entry in dups_to_process:
            refid = entry["refid"]
            etype = entry["type"]
            
            if refid not in refid_dups:
                continue

            if refid in self._refids_to_ignore:
                continue

            if refid not in transactions:
                transactions[refid] = {}
                transactions[refid]["raw"] = []
                transactions[refid]["types"] = []
                transactions[refid]["meta"] = {}

            transactions[refid]["raw"].append(entry)
            transactions[refid]["types"].append(etype)
            transactions[refid]["meta"]["parsing_info"] = "dup"

        # Process transactions classified as dups which have a missing refid
        unknown_nondups = []
        if "Unknown" in transactions:
            unknown_transactions = transactions["Unknown"]
            del transactions["Unknown"]

            # unknown_dups can be ignored, they are transactions that add and subtract same amount of same asset
            # let's search for unknown nondups, which are real transactions with wrong refid due to a Kraken bug.

            unknown_df = pd.DataFrame(unknown_transactions.get("raw", []))
            unknown_df["abs_amount"] = unknown_df["amount"].apply(self.__get_abs_amount)
            unknown_df["norm_asset"] = unknown_df["asset"].apply(self.__normalize_currency_abbreviation)
            unknown_nondups = unknown_df.groupby(["abs_amount", "norm_asset"], as_index=False).agg({'txid':'first', 'refid':'count'})
            unknown_nondups = unknown_nondups[unknown_nondups["refid"] < 2]
            unknown_nondups = list(unknown_nondups["txid"])

            unknown_nondups_to_process = list(filter(lambda item: item["txid"] in unknown_nondups, raw_ledger))
            for entry in unknown_nondups_to_process:
                entry["refid"] = entry["txid"]
                refid = entry["refid"]

                if refid not in transactions:
                    transactions[refid] = {}
                    transactions[refid]["raw"] = []
                    transactions[refid]["types"] = []
                    transactions[refid]["meta"] = {}

                    transactions[refid]["raw"].append(entry)
                    transactions[refid]["types"].append(etype)
                    transactions[refid]["meta"]["parsing_info"] = "nondup"
                else:
                    pass  # It is enough to add these once, as they are the same entry twice

        def dupfilter(item):
            return item["refid"] not in refid_dups and item["refid"] != "Unknown"
        
        nondups_to_process = list(filter(dupfilter, raw_ledger))
        for entry in nondups_to_process:
            refid = entry["refid"]
            etype = entry["type"]
            txid = entry["txid"]
            time = entry["time"]
            date = entry["Date"]
            
            asset = entry["asset"]
            amount = entry["amount"]

            if refid in self._refids_to_ignore:
                continue

            found_matching_transactions = refid in unknown_nondups

            for other_entry in nondups_to_process:
                other_refid = other_entry["refid"]
                other_etype = other_entry["type"]
                other_txid = other_entry["txid"]
                other_time = other_entry["time"]
                other_date = other_entry["Date"]

                if refid == other_refid and txid == other_txid and etype == other_etype and time == other_time:
                    # Skip same entry
                    continue

                other_asset = other_entry["asset"]
                other_amount = other_entry["amount"]

                if asset == other_asset and amount == other_amount and date == other_date:

                    # TODO: Could additionally check for transactions within a few minutes

                    new_key = f"{asset}_{amount}"

                    found_matching_transactions = True

                    refid = refid if refid else other_refid

                    if refid not in transactions:
                        transactions[new_key] = {}
                        transactions[new_key]["raw"] = []
                        transactions[new_key]["types"] = []
                        transactions[new_key]["meta"] = {}

                    transactions[new_key]["raw"].append(entry)
                    transactions[new_key]["raw"].append(other_entry)

                    transactions[new_key]["types"].append(etype)
                    transactions[new_key]["types"].append(other_etype)

                    transactions[new_key]["meta"]["parsing_info"] = "dup_asset_amount_match"
                
            if not found_matching_transactions:

                if refid not in transactions:
                    transactions[refid] = {}
                    transactions[refid]["raw"] = []
                    transactions[refid]["types"] = []
                    transactions[refid]["meta"] = {}

                transactions[refid]["raw"].append(entry)
                transactions[refid]["types"].append(etype)
                transactions[refid]["meta"]["parsing_info"] = "nondup"

        return transactions
