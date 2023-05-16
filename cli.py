# -*- coding: utf-8 -*-
"""
CLI adapter for LedgerProcessor

Copyright 2022-05-16 AlexanderLill
"""
import argparse
import json

from src.portfolio_performance_rate_provider import PortfolioPerformanceRateProvider
from src.ledger_processor import LedgerProcessor

parser = argparse.ArgumentParser(description='Parse Kraken Crypto Transactions for Portfolio Performance Import.')


### Rate Provider
parser.add_argument('pp_rates_file', metavar='PP_RATES_FILE', type=str, nargs='?',
                    help='portfolio performance rates export')
parser.add_argument('-cm', '--currency-mapping', dest='currency_mapping', type=json.loads)


### Ledger Processor
parser.add_argument('kraken_csv_file', metavar='KRAKEN_CSV_FILE', type=str, nargs='?',
                    help='kraken ledger export csv file')
parser.add_argument('-fc', '--fiat-currency', dest="fiat_currency", help='define base currency (def=EUR)', default='EUR')
parser.add_argument('-ir', '--ignore-refids', dest='refids_to_ignore', type=str, help="Comma-separated list of refids to ignore while processing", default="")
parser.add_argument('-o', '--out-dir', dest='out_dir', type=str, help='Directory to store PP transactions in (def=cwd)', default='.')
parser.add_argument('-do', '--depot-old', dest='depot_old', type=str, help="Name of current/old depot (def=DEPOT)", default="DEPOT")
parser.add_argument('-dn', '--depot-new', dest='depot_new', type=str, help="Name of new depot (target of transfers, def=DEPOT_NEW)", default="DEPOT_NEW")
parser.add_argument('-a', '--account', dest='account', type=str, help="Name of account, def=ACCOUNT", default="ACCOUNT")
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', help='Activate verbose mode')

args = parser.parse_args()

if args.verbose:
    print(args)

if args.pp_rates_file:
    rate_provider = PortfolioPerformanceRateProvider(args.pp_rates_file,
                                                     currency_mapping=args.currency_mapping,
                                                     fiat_currency=args.fiat_currency)
else:
    rate_provider = None

lp = LedgerProcessor(filename=args.kraken_csv_file,
                     rate_provider=rate_provider,
                     fiat_currency=args.fiat_currency,
                     refids_to_ignore=args.refids_to_ignore,
                     depot_current=args.depot_old,
                     depot_new=args.depot_new,
                     account=args.account)

lp.store_depot_normal_transactions(f"{args.out_dir}/transactions_normal_depot.csv")
lp.store_depot_special_transactions(f"{args.out_dir}/transactions_special_depot.csv")
lp.store_account_transactions(f"{args.out_dir}/transactions_account.csv")
