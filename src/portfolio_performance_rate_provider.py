# -*- coding: utf-8 -*-
"""
PortfolioPerformanceRateProvider

Copyright 2022-05-16 AlexanderLill
"""
import datetime
import pandas as pd
import locale

class PortfolioPerformanceRateProvider:
    def __init__(self, export_file, fiat_currency="EUR", time_format="%Y-%m-%d %H:%M:%S", language="de", currency_mapping=None):
        if language == "de":
            self._thousands = "."
            self._decimal = ","
            self._sep = ";"
        if language == "en":
            self._thousands = ","
            self._decimal = "."
            self._sep = ","
        self._export_file = export_file
        self._fiat_currency = fiat_currency
        self._time_format = time_format
        self.__df = pd.read_csv(export_file, sep=self._sep, index_col=0, parse_dates=[0], thousands=self._thousands, decimal=self._decimal)
        if currency_mapping is not None:
            self.__df.rename(columns=currency_mapping, inplace=True)
        locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')  # TODO: Cleanup locale stuff

    def get_rate(self, crypto_currency, timestr=None, timeobj=None):
        
        if timestr:
            t = datetime.datetime.strptime(timestr, self._time_format)
        
        if timeobj:
            t = timeobj
        
        formatted_datetime = t.strftime("%Y-%m-%d")
        column_name = f"{crypto_currency}-{self._fiat_currency}"

        if formatted_datetime in self.__df.index:
            row = self.__df.loc[formatted_datetime]
        else:
            raise ValueError(f'Could not find rate for date {formatted_datetime} (currency={column_name})')

        if column_name in row:
            rate = row[column_name]
        else:
            raise ValueError(f'Could not find rate for currency {column_name} in export loaded from {self._export_file}\nFound columns: ' + "\n".join(self.__df.columns))

        # TODO: Cleanup locale stuff
        # rate = rate.replace(self._thousands, "")  # Need to remove thousands-sep, locale stuff does not work ... 15.426,75
        # return locale.atof(rate)
        return rate
