# -*- coding: utf-8 -*-
"""
Unit test for the PortfolioPerformanceRateProvider module

Copyright 2022-05-16 AlexanderLill
"""
import unittest

from src.portfolio_performance_rate_provider import PortfolioPerformanceRateProvider

class PortfolioPerformanceRateProviderTest(unittest.TestCase):
    PORTFOLIO_PERFORMANCE_RATES_EXPORT_FILE = "./testdata/Alle_historischen_Kurse.csv"
    TEST_CURRENCY = "BTC"
    TEST_TIMESTAMP = "2022-12-31 20:46:17"
    TEST_EXPECTED_RATE = 15426.75

    def test_get_btc_rate_for_day(self):
        rp = PortfolioPerformanceRateProvider(self.PORTFOLIO_PERFORMANCE_RATES_EXPORT_FILE)
        result = rp.get_rate(self.TEST_CURRENCY, self.TEST_TIMESTAMP)
        self.assertEquals(result, self.TEST_EXPECTED_RATE)
    
    def test_get_rate_for_unavailable_currency(self):
        rp = PortfolioPerformanceRateProvider(self.PORTFOLIO_PERFORMANCE_RATES_EXPORT_FILE)
        self.assertRaises(ValueError, rp.get_rate, *("UNKNOWN", self.TEST_TIMESTAMP))
    
    def test_get_rate_for_unavailable_date(self):
        rp = PortfolioPerformanceRateProvider(self.PORTFOLIO_PERFORMANCE_RATES_EXPORT_FILE)
        self.assertRaises(ValueError, rp.get_rate, *(self.TEST_CURRENCY, "1970-01-01 00:00:00"))

    def test_currency_mapping(self):
        FICTICIOUS_CURRENCY = "ALIASCOIN"

        rp_orig = PortfolioPerformanceRateProvider(self.PORTFOLIO_PERFORMANCE_RATES_EXPORT_FILE)
        self.assertRaises(ValueError, rp_orig.get_rate, *(FICTICIOUS_CURRENCY, self.TEST_TIMESTAMP))
        
        rp_mapped = PortfolioPerformanceRateProvider(self.PORTFOLIO_PERFORMANCE_RATES_EXPORT_FILE,
                                                     currency_mapping={"BTC-EUR": f"{FICTICIOUS_CURRENCY}-EUR"})
        result = rp_mapped.get_rate(FICTICIOUS_CURRENCY, self.TEST_TIMESTAMP)
        self.assertEquals(result, self.TEST_EXPECTED_RATE)
