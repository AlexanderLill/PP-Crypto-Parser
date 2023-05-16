# -*- coding: utf-8 -*-
"""
Unit test for the LedgerProcessor module

Copyright 2022-05-16 AlexanderLill
"""
import os
from io import StringIO
import unittest
import pandas as pd
from textwrap import dedent


from src.ledger_processor import LedgerProcessor
from src.portfolio_performance_rate_provider import PortfolioPerformanceRateProvider


class LedgerProcessorTest(unittest.TestCase):
    """Test case implementation for PeerToPeerPlatformParser"""

    def setUp(self):
        """test case setUp, run for each test case"""
        self.maxDiff = None
        
        self.DEPOT_CURRENT = "DEPOT"
        self.DEPOT_NEW = "DEPOT_NEW"
        self.ACCOUNT = "ACCOUNT"

        class MockRateProvider:
            def get_rate(self, crypto_currency, timestr=None, timeobj=None):
                return 100.00

        self.rate_provider = MockRateProvider()

    def test_import_deposit_fiat(self):
        kraken_csv = dedent("""
        "txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
        "","QCCA6ZN-5V5YRZ-GFXN7W","2020-12-31 06:14:02","deposit","","currency","ZEUR",1000.0000,0.0000,""
        "LYOM2B-J6VD2-YRYBOA","QCCA6ZN-5V5YRZ-GFXN7W","2020-12-31 06:14:54","deposit","","currency","ZEUR",1000.0000,0.0000,10581.8771
        "","QYSDQAQ-CAVS3A-CHE2MA","2022-12-19 09:10:00","deposit","","currency","ZEUR",500.0000,0.0000,""
        "LSTC6E-NHFSO-O2MWRN","QYSDQAQ-CAVS3A-CHE2MA","2022-12-19 09:17:22","deposit","","currency","ZEUR",500.0000,0.0000,500.0014
        """)

        expected_account_csv = dedent("""
        2020-12-31;06:14:54;Einlage;1.000,000000;;;;;;QCCA6ZN-5V5YRZ-GFXN7W,LYOM2B-J6VD2-YRYBOA;
        2022-12-19;09:17:22;Einlage;500,000000;;;;;;QYSDQAQ-CAVS3A-CHE2MA,LSTC6E-NHFSO-O2MWRN;
        """)

        df = pd.read_csv(StringIO(kraken_csv))
        
        lp = LedgerProcessor(dataframe=df, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        transactions = lp.get_transactions()

        at = transactions["account_transactions"]
        self.assertEquals(len(at), 2)

        self.assertEquals(at[0].amount, 1000.00)
        self.assertEquals(at[1].amount, 500.00)

        result_csv = "\n"
        for t in at:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_account_csv)

    def test_import_deposit_crypto_norate(self):
        kraken_csv = dedent("""
        "txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
        "","QGEAOWO-KDDLPS-SEZYR4","2020-12-27 10:49:55","deposit","","currency","XETH",0.0456499600,0.0000000000,""
        "LI23O6-3HOWX-H7ABRD","QGEAOWO-KDDLPS-SEZYR4","2020-12-27 14:20:35","deposit","","currency","XETH",0.0456499600,0.0000000000,0.0456499600
        "","QGBC2MD-Z6DOQG-6XCKRU","2020-12-27 15:24:07","deposit","","currency","XXBT",0.0032526300,0.0000000000,""
        "LIPGMF-SWNWY-AQ3LKF","QGBC2MD-Z6DOQG-6XCKRU","2020-12-27 18:04:03","deposit","","currency","XXBT",0.0032526300,0.0000000000,0.0032526300
        """)

        expected_depot_csv = dedent("""
        2020-12-27;18:04:03;Einlieferung;XBT;0,003253;DUMMYRATE;DUMMYVAL;;;DUMMYTOTAL;DEPOT;;QGBC2MD-Z6DOQG-6XCKRU,LIPGMF-SWNWY-AQ3LKF;
        2020-12-27;14:20:35;Einlieferung;ETH;0,045650;DUMMYRATE;DUMMYVAL;;;DUMMYTOTAL;DEPOT;;QGEAOWO-KDDLPS-SEZYR4,LI23O6-3HOWX-H7ABRD;
        """)

        df = pd.read_csv(StringIO(kraken_csv))
        
        lp = LedgerProcessor(dataframe=df, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        transactions = lp.get_transactions()

        dt = transactions["depot_special_transactions"]

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_depot_csv)
    
    def test_import_deposit_crypto_withrate(self):
        kraken_csv = dedent("""
        "txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
        "","QGEAOWO-KDDLPS-SEZYR4","2020-12-27 10:49:55","deposit","","currency","XETH",0.0456499600,0.0000000000,""
        "LI23O6-3HOWX-H7ABRD","QGEAOWO-KDDLPS-SEZYR4","2020-12-27 14:20:35","deposit","","currency","XETH",0.0456499600,0.0000000000,0.0456499600
        "","QGBC2MD-Z6DOQG-6XCKRU","2020-12-27 15:24:07","deposit","","currency","XXBT",0.0032526300,0.0000000000,""
        "LIPGMF-SWNWY-AQ3LKF","QGBC2MD-Z6DOQG-6XCKRU","2020-12-27 18:04:03","deposit","","currency","XXBT",0.0032526300,0.0000000000,0.0032526300
        """)

        expected_depot_csv = dedent("""
        2020-12-27;18:04:03;Einlieferung;XBT;0,003253;100,000000;0,325263;;;0,325263;DEPOT;;QGBC2MD-Z6DOQG-6XCKRU,LIPGMF-SWNWY-AQ3LKF;
        2020-12-27;14:20:35;Einlieferung;ETH;0,045650;100,000000;4,564996;;;4,564996;DEPOT;;QGEAOWO-KDDLPS-SEZYR4,LI23O6-3HOWX-H7ABRD;
        """)

        df = pd.read_csv(StringIO(kraken_csv))
        
        lp = LedgerProcessor(dataframe=df, rate_provider=self.rate_provider, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        transactions = lp.get_transactions()

        dt = transactions["depot_special_transactions"]

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_depot_csv)

    def test_import_buy(self):
        kraken_csv = dedent("""
        "txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
        "LU4MDZ-PSSAV-7KKYF2","TTWFFE-HZX34-2EEGRM","2022-02-24 08:57:02","trade","","currency","ZEUR",-1499.9999,2.4000,793.5752
        "L3H4BL-PFLZU-JVX2JY","TTWFFE-HZX34-2EEGRM","2022-02-24 08:57:02","trade","","currency","XXBT",0.0474606900,0.0000000000,0.0474667000
        """)

        expected_depot_csv = dedent("""
        2022-02-24;08:57:02;Kauf;XBT;0,047461;31.605,100979;1.499,999900;2,400000;;1.502,399900;DEPOT;ACCOUNT;TTWFFE-HZX34-2EEGRM,L3H4BL-PFLZU-JVX2JY,LU4MDZ-PSSAV-7KKYF2;
        """)

        df = pd.read_csv(StringIO(kraken_csv))
        
        lp = LedgerProcessor(dataframe=df, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        transactions = lp.get_transactions()

        dt = transactions["depot_normal_transactions"]

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_depot_csv)
    
    def test_import_spend_receive(self):
        kraken_csv = dedent("""
        "txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
        "LITOLA-QGBFJ-GS4SHT","TSS6BTF-K6OZK-DZ6MUU","2020-12-29 16:39:51","spend","","currency","ZEUR",-500.0000,0.0000,10581.8771
        "LT466K-ML25G-HZUBFW","TSS6BTF-K6OZK-DZ6MUU","2020-12-29 16:39:51","receive","","currency","DOT",4633.18411000,0.00000000,4633.18411000
        "LWMW4D-2SD5X-ZQFL36","TSROARZ-BQ3DZ-JNK5UX","2020-12-29 16:44:32","spend","","currency","ZEUR",-500.0000,0.0000,10081.8771
        "LOZOFF-7GM63-NYY5XN","TSROARZ-BQ3DZ-JNK5UX","2020-12-29 16:44:32","receive","","currency","XETH",0.8489400000,0.0000000000,0.8489400000
        """)

        expected_depot_csv = dedent("""
        2020-12-29;16:44:32;Kauf;ETH;0,848940;588,969774;500,000000;;;500,000000;DEPOT;ACCOUNT;TSROARZ-BQ3DZ-JNK5UX,LOZOFF-7GM63-NYY5XN,LWMW4D-2SD5X-ZQFL36;
        2020-12-29;16:39:51;Kauf;DOT;4.633,184110;0,107917;500,000000;;;500,000000;DEPOT;ACCOUNT;TSS6BTF-K6OZK-DZ6MUU,LITOLA-QGBFJ-GS4SHT,LT466K-ML25G-HZUBFW;
        """)

        df = pd.read_csv(StringIO(kraken_csv))
        
        lp = LedgerProcessor(dataframe=df, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        transactions = lp.get_transactions()

        dt = transactions["depot_normal_transactions"]
        dt = sorted(dt,key=lambda t: t.date)

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_depot_csv)
    
    def test_import_withdrawal_fiat(self):
        kraken_csv = dedent("""
        "txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
        "","ACC3OMW-HGUTIZ-YWRQ5G","2021-01-22 11:02:47","withdrawal","","currency","ZEUR",-1000.0000,0.0900,""
        "LLMXLS-24H3J-YIAPGT","ACC3OMW-HGUTIZ-YWRQ5G","2021-01-22 11:05:43","withdrawal","","currency","ZEUR",-1000.0000,0.0900,2118.2448
        "","ACCQI32-CXZBGN-TFSLML","2022-10-22 17:16:55","withdrawal","","currency","ZEUR",-150.0500,0.0900,""
        "LFZVWD-SOZQ5-QXSC2W","ACCQI32-CXZBGN-TFSLML","2022-10-22 17:18:34","withdrawal","","currency","ZEUR",-150.0500,0.0900,0.0013
        """)

        expected_account_csv = dedent("""  
        2021-01-22;11:05:43;Entnahme;1.000,000000;;;;;;ACC3OMW-HGUTIZ-YWRQ5G,LLMXLS-24H3J-YIAPGT;
        2021-01-22;11:05:43;Gebühren;0,090000;;;;;;ACC3OMW-HGUTIZ-YWRQ5G,LLMXLS-24H3J-YIAPGT;
        2022-10-22;17:18:34;Entnahme;150,050000;;;;;;ACCQI32-CXZBGN-TFSLML,LFZVWD-SOZQ5-QXSC2W;
        2022-10-22;17:18:34;Gebühren;0,090000;;;;;;ACCQI32-CXZBGN-TFSLML,LFZVWD-SOZQ5-QXSC2W;
        """)

        df = pd.read_csv(StringIO(kraken_csv))
        
        lp = LedgerProcessor(dataframe=df, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        transactions = lp.get_transactions()

        dt = transactions["account_transactions"]
        dt = sorted(dt,key=lambda t: t.date)

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_account_csv)

    def test_import_withdrawal_crypto_norate(self):
        kraken_csv = dedent("""
        "txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
        "","AGB76R3-DWC5SC-UCBGGX","2021-11-03 20:15:19","withdrawal","","currency","XXBT",-0.0307600000,0.0001500000,""
        "LU6WLT-MWUUY-BVWZ6E","AGB76R3-DWC5SC-UCBGGX","2021-11-03 21:02:37","withdrawal","","currency","XXBT",-0.0307600000,0.0001500000,0.0000060100
        "","A2BEPJY-DA4STX-EUIDDR","2021-11-03 20:42:17","withdrawal","","currency","XETH",-0.3596600000,0.0035000000,""
        "LZUN3G-CKFHJ-SPCPCB","A2BEPJY-DA4STX-EUIDDR","2021-11-03 20:46:17","withdrawal","","currency","XETH",-0.3596600000,0.0035000000,0.0000056800
        "","BSIEEVZ-2KMYBJ-VMCTBB","2021-11-03 20:44:02","withdrawal","","currency","DOT",-36.1477171000,0.0500000000,""
        "LISGE7-RAPDY-QMZ626","BSIEEVZ-2KMYBJ-VMCTBB","2021-11-03 21:13:25","withdrawal","","currency","DOT",-36.1477171000,0.0500000000,0.0000000000
        """)

        expected_depot_csv = dedent("""
        2021-11-03;20:46:17;Umbuchung (Ausgang);ETH;0,359660;DUMMYRATE;DUMMYVAL;;;DUMMYTOTAL;DEPOT;DEPOT_NEW;A2BEPJY-DA4STX-EUIDDR,LZUN3G-CKFHJ-SPCPCB;
        2021-11-03;20:46:17;Verkauf;ETH;0,003500;DUMMYRATE;DUMMYFEES;;;DUMMYFEES;DEPOT;ACCOUNT;A2BEPJY-DA4STX-EUIDDR,LZUN3G-CKFHJ-SPCPCB;
        2021-11-03;21:02:37;Umbuchung (Ausgang);XBT;0,030760;DUMMYRATE;DUMMYVAL;;;DUMMYTOTAL;DEPOT;DEPOT_NEW;AGB76R3-DWC5SC-UCBGGX,LU6WLT-MWUUY-BVWZ6E;
        2021-11-03;21:02:37;Verkauf;XBT;0,000150;DUMMYRATE;DUMMYFEES;;;DUMMYFEES;DEPOT;ACCOUNT;AGB76R3-DWC5SC-UCBGGX,LU6WLT-MWUUY-BVWZ6E;
        2021-11-03;21:13:25;Umbuchung (Ausgang);DOT;36,147717;DUMMYRATE;DUMMYVAL;;;DUMMYTOTAL;DEPOT;DEPOT_NEW;BSIEEVZ-2KMYBJ-VMCTBB,LISGE7-RAPDY-QMZ626;
        2021-11-03;21:13:25;Verkauf;DOT;0,050000;DUMMYRATE;DUMMYFEES;;;DUMMYFEES;DEPOT;ACCOUNT;BSIEEVZ-2KMYBJ-VMCTBB,LISGE7-RAPDY-QMZ626;
        """)

        expected_account_csv = dedent("""
        2021-11-03;20:46:17;Gebühren;DUMMYFEES;;ETH;;;;A2BEPJY-DA4STX-EUIDDR,LZUN3G-CKFHJ-SPCPCB;
        2021-11-03;21:02:37;Gebühren;DUMMYFEES;;XBT;;;;AGB76R3-DWC5SC-UCBGGX,LU6WLT-MWUUY-BVWZ6E;
        2021-11-03;21:13:25;Gebühren;DUMMYFEES;;DOT;;;;BSIEEVZ-2KMYBJ-VMCTBB,LISGE7-RAPDY-QMZ626;
        """)

        df = pd.read_csv(StringIO(kraken_csv))
        
        lp = LedgerProcessor(dataframe=df, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        transactions = lp.get_transactions()

        dt = transactions["depot_normal_transactions"]
        dt = sorted(dt,key=lambda t: t.date)

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_depot_csv)

        dt = transactions["account_transactions"]
        dt = sorted(dt,key=lambda t: t.date)

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_account_csv)
    
    def test_import_withdrawal_crypto_withrate(self):
        kraken_csv = dedent("""
        "txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
        "","AGB76R3-DWC5SC-UCBGGX","2021-11-03 20:15:19","withdrawal","","currency","XXBT",-0.0307600000,0.0001500000,""
        "LU6WLT-MWUUY-BVWZ6E","AGB76R3-DWC5SC-UCBGGX","2021-11-03 21:02:37","withdrawal","","currency","XXBT",-0.0307600000,0.0001500000,0.0000060100
        "","A2BEPJY-DA4STX-EUIDDR","2021-11-03 20:42:17","withdrawal","","currency","XETH",-0.3596600000,0.0035000000,""
        "LZUN3G-CKFHJ-SPCPCB","A2BEPJY-DA4STX-EUIDDR","2021-11-03 20:46:17","withdrawal","","currency","XETH",-0.3596600000,0.0035000000,0.0000056800
        "","BSIEEVZ-2KMYBJ-VMCTBB","2021-11-03 20:44:02","withdrawal","","currency","DOT",-36.1477171000,0.0500000000,""
        "LISGE7-RAPDY-QMZ626","BSIEEVZ-2KMYBJ-VMCTBB","2021-11-03 21:13:25","withdrawal","","currency","DOT",-36.1477171000,0.0500000000,0.0000000000
        """)

        expected_depot_csv = dedent("""
        2021-11-03;20:46:17;Umbuchung (Ausgang);ETH;0,359660;100,000000;35,966000;;;35,966000;DEPOT;DEPOT_NEW;A2BEPJY-DA4STX-EUIDDR,LZUN3G-CKFHJ-SPCPCB;
        2021-11-03;20:46:17;Verkauf;ETH;0,003500;100,000000;0,350000;;;0,350000;DEPOT;ACCOUNT;A2BEPJY-DA4STX-EUIDDR,LZUN3G-CKFHJ-SPCPCB;
        2021-11-03;21:02:37;Umbuchung (Ausgang);XBT;0,030760;100,000000;3,076000;;;3,076000;DEPOT;DEPOT_NEW;AGB76R3-DWC5SC-UCBGGX,LU6WLT-MWUUY-BVWZ6E;
        2021-11-03;21:02:37;Verkauf;XBT;0,000150;100,000000;0,015000;;;0,015000;DEPOT;ACCOUNT;AGB76R3-DWC5SC-UCBGGX,LU6WLT-MWUUY-BVWZ6E;
        2021-11-03;21:13:25;Umbuchung (Ausgang);DOT;36,147717;100,000000;3.614,771710;;;3.614,771710;DEPOT;DEPOT_NEW;BSIEEVZ-2KMYBJ-VMCTBB,LISGE7-RAPDY-QMZ626;
        2021-11-03;21:13:25;Verkauf;DOT;0,050000;100,000000;5,000000;;;5,000000;DEPOT;ACCOUNT;BSIEEVZ-2KMYBJ-VMCTBB,LISGE7-RAPDY-QMZ626;
        """)

        expected_account_csv = dedent("""
        2021-11-03;20:46:17;Gebühren;0,350000;;ETH;;;;A2BEPJY-DA4STX-EUIDDR,LZUN3G-CKFHJ-SPCPCB;
        2021-11-03;21:02:37;Gebühren;0,015000;;XBT;;;;AGB76R3-DWC5SC-UCBGGX,LU6WLT-MWUUY-BVWZ6E;
        2021-11-03;21:13:25;Gebühren;5,000000;;DOT;;;;BSIEEVZ-2KMYBJ-VMCTBB,LISGE7-RAPDY-QMZ626;
        """)

        df = pd.read_csv(StringIO(kraken_csv))
        
        lp = LedgerProcessor(dataframe=df, rate_provider=self.rate_provider, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        transactions = lp.get_transactions()

        dt = transactions["depot_normal_transactions"]
        dt = sorted(dt,key=lambda t: t.date)

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_depot_csv)

        dt = transactions["account_transactions"]
        dt = sorted(dt,key=lambda t: t.date)

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_account_csv)
    
    def test_import_staking_norate(self):
        kraken_csv = dedent("""
        "txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
        "","RUGLWVG-XQGB5M-MHHHL7","2022-12-11 01:03:09","deposit","","currency","ATOM.S",0.00344300,0.00000000,""
        "L4U7Y4-WP76L-34UMSV","STFCFLD-65INO-G3O54V","2022-12-11 03:41:47","staking","","currency","ATOM.S",0.00344300,0.00000000,2.09972400
        "","RU22CDD-HYY3TA-7BUTL7","2022-12-06 02:02:17","deposit","","currency","TRX.S",0.03123500,0.00000000,""
        "LKHJDB-EZBTS-F3R5P4","STXGL5M-OJNJC-LTUA35","2022-12-06 05:12:33","staking","","currency","TRX.S",0.03123500,0.00000000,758.20002200
        """)

        expected_depot_csv = dedent("""
        2022-12-06;05:12:33;Einlieferung;TRX;0,031235;DUMMYRATE;DUMMYVAL;;;DUMMYTOTAL;DEPOT;;RU22CDD-HYY3TA-7BUTL7,STXGL5M-OJNJC-LTUA35,LKHJDB-EZBTS-F3R5P4;
        2022-12-11;03:41:47;Einlieferung;ATOM;0,003443;DUMMYRATE;DUMMYVAL;;;DUMMYTOTAL;DEPOT;;RUGLWVG-XQGB5M-MHHHL7,STFCFLD-65INO-G3O54V,L4U7Y4-WP76L-34UMSV;
        """)

        df = pd.read_csv(StringIO(kraken_csv))
        
        lp = LedgerProcessor(dataframe=df, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        transactions = lp.get_transactions()

        dt = transactions["depot_special_transactions"]
        dt = sorted(dt,key=lambda t: t.date)

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_depot_csv)

    def test_import_staking_withrate(self):
        kraken_csv = dedent("""
        "txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
        "","RUGLWVG-XQGB5M-MHHHL7","2022-12-11 01:03:09","deposit","","currency","ATOM.S",0.00344300,0.00000000,""
        "L4U7Y4-WP76L-34UMSV","STFCFLD-65INO-G3O54V","2022-12-11 03:41:47","staking","","currency","ATOM.S",0.00344300,0.00000000,2.09972400
        "","RU22CDD-HYY3TA-7BUTL7","2022-12-06 02:02:17","deposit","","currency","TRX.S",0.03123500,0.00000000,""
        "LKHJDB-EZBTS-F3R5P4","STXGL5M-OJNJC-LTUA35","2022-12-06 05:12:33","staking","","currency","TRX.S",0.03123500,0.00000000,758.20002200
        """)

        expected_depot_csv = dedent("""
        2022-12-06;05:12:33;Einlieferung;TRX;0,031235;100,000000;3,123500;;;3,123500;DEPOT;;RU22CDD-HYY3TA-7BUTL7,STXGL5M-OJNJC-LTUA35,LKHJDB-EZBTS-F3R5P4;
        2022-12-11;03:41:47;Einlieferung;ATOM;0,003443;100,000000;0,344300;;;0,344300;DEPOT;;RUGLWVG-XQGB5M-MHHHL7,STFCFLD-65INO-G3O54V,L4U7Y4-WP76L-34UMSV;
        """)

        df = pd.read_csv(StringIO(kraken_csv))
        
        lp = LedgerProcessor(dataframe=df, rate_provider=self.rate_provider, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        transactions = lp.get_transactions()

        dt = transactions["depot_special_transactions"]
        dt = sorted(dt,key=lambda t: t.date)

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_depot_csv)
    
    def test_creation_of_extra_fee_transactions(self):
        kraken_csv = dedent("""
        "txid","refid","time","type","subtype","aclass","asset","amount","fee","balance"
        "L2BWE5-NBPJB-NIWB5S","TBCS6K-4RXM6-MGRNUC","2022-02-24 09:00:02","trade","","currency","ZEUR",-693.0000,0.2337,100.3415
        "LLPJSO-KWCYV-ZCXUIN","TBCS6K-4RXM6-MGRNUC","2022-02-24 09:00:02","trade","","currency","DOT",54.0038729800,0.1222000600,53.8816729200
        """)

        expected_depot_csv = dedent("""
        2022-02-24;09:00:02;Kauf;DOT;54,003873;12,832413;693,000000;0,233700;;693,233700;DEPOT;ACCOUNT;TBCS6K-4RXM6-MGRNUC,L2BWE5-NBPJB-NIWB5S,LLPJSO-KWCYV-ZCXUIN;
        2022-02-24;09:00:02;Verkauf;DOT;0,122200;12,832413;1,568122;;;1,568122;DEPOT;ACCOUNT;TBCS6K-4RXM6-MGRNUC,L2BWE5-NBPJB-NIWB5S,LLPJSO-KWCYV-ZCXUIN;
        """)

        expected_account_csv = dedent("""
        2022-02-24;09:00:02;Gebühren;1,568122;;DOT;;;;TBCS6K-4RXM6-MGRNUC,L2BWE5-NBPJB-NIWB5S,LLPJSO-KWCYV-ZCXUIN;
        """)

        df = pd.read_csv(StringIO(kraken_csv))
        
        lp = LedgerProcessor(dataframe=df, rate_provider=self.rate_provider, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        transactions = lp.get_transactions()

        dt = transactions["depot_normal_transactions"]
        dt = sorted(dt,key=lambda t: t.date)

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_depot_csv)

        dt = transactions["account_transactions"]
        dt = sorted(dt,key=lambda t: t.date)

        result_csv = "\n"
        for t in dt:
            result_csv = result_csv + t.to_csv() + "\n"

        self.assertEquals(result_csv, expected_account_csv)

    def test_pipeline(self):
        KRAKEN_INPUT_FILE = "./testdata/kraken_withdrawal.csv"
        PORTFOLIO_PERFORMANCE_RATE_EXPORT = "./testdata/Alle_historischen_Kurse.csv"

        DEPOT_NORMAL_OUTPUT_OBSERVED_FILE = "./testdata/kraken_withdrawal_depot_normal_obs.csv"
        DEPOT_SPECIAL_OUTPUT_OBSERVED_FILE = "./testdata/kraken_withdrawal_depot_special_obs.csv"
        ACCOUNT_OUTPUT_OBSERVED_FILE = "./testdata/kraken_withdrawal_account_obs.csv"

        DEPOT_NORMAL_OUTPUT_EXPECTED_FILE = "./testdata/kraken_withdrawal_depot_normal_exp.csv"
        DEPOT_SPECIAL_OUTPUT_EXPECTED_FILE = "./testdata/kraken_withdrawal_depot_special_exp.csv"
        ACCOUNT_OUTPUT_EXPECTED_FILE = "./testdata/kraken_withdrawal_account_exp.csv"

        def __delete_observed_files():
            if os.path.isfile(DEPOT_NORMAL_OUTPUT_OBSERVED_FILE):
                os.remove(DEPOT_NORMAL_OUTPUT_OBSERVED_FILE)
            
            if os.path.isfile(DEPOT_SPECIAL_OUTPUT_OBSERVED_FILE):
                os.remove(DEPOT_SPECIAL_OUTPUT_OBSERVED_FILE)
            
            if os.path.isfile(ACCOUNT_OUTPUT_OBSERVED_FILE):
                os.remove(ACCOUNT_OUTPUT_OBSERVED_FILE)
        
        __delete_observed_files()

        rate_provider = PortfolioPerformanceRateProvider(PORTFOLIO_PERFORMANCE_RATE_EXPORT,
                                                         currency_mapping={"BTC-EUR": "XBT-EUR"})

        lp = LedgerProcessor(filename=KRAKEN_INPUT_FILE, rate_provider=rate_provider, depot_current=self.DEPOT_CURRENT, depot_new=self.DEPOT_NEW, account=self.ACCOUNT)
        lp.store_depot_normal_transactions(DEPOT_NORMAL_OUTPUT_OBSERVED_FILE)
        lp.store_depot_special_transactions(DEPOT_SPECIAL_OUTPUT_OBSERVED_FILE)
        lp.store_account_transactions(ACCOUNT_OUTPUT_OBSERVED_FILE)

        depot_normal_obs = pd.read_csv(DEPOT_NORMAL_OUTPUT_OBSERVED_FILE, sep=";")
        depot_normal_exp = pd.read_csv(DEPOT_NORMAL_OUTPUT_EXPECTED_FILE, sep=";")

        depot_special_obs = pd.read_csv(DEPOT_SPECIAL_OUTPUT_OBSERVED_FILE, sep=";")
        depot_special_exp = pd.read_csv(DEPOT_SPECIAL_OUTPUT_EXPECTED_FILE, sep=";")

        account_obs = pd.read_csv(ACCOUNT_OUTPUT_OBSERVED_FILE, sep=";")
        account_exp = pd.read_csv(ACCOUNT_OUTPUT_EXPECTED_FILE, sep=";")

        __delete_observed_files()

        self.assertTrue(depot_normal_obs.equals(depot_normal_exp))
        self.assertTrue(depot_special_obs.equals(depot_special_exp))
        self.assertTrue(account_obs.equals(account_exp))
