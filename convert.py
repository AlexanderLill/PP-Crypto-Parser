from os import sep
import pandas as pd

def create_dateandtime(row):
    row["Date"] = row["time"].split()[0]
    row["Time"] = row["time"].split()[1].split(".")[0]
    return row

def calculate_value(row):
    transaction_type = row["type"]

    if transaction_type == "buy":
        row["Value"] = "{0:.8f}".format(float(row["cost"]) + float(row["fee"]))
    elif transaction_type == "sell":
        row["Value"] = "{0:.8f}".format(float(row["cost"]) - float(row["fee"]))
    else:
        print("Unknown transaction_type: {}".format(transaction_type))
    return row

def map_pair(pairname):
    kraken_pp_map = {
        "AVAXEUR": "AVAX",
        "ADAEUR": "ADA",
        "ALGOEUR": "ALGO",
        "ATOMEUR": "ATOM",
        "BCHEUR": "BCH",
        "DOTEUR": "DOT",
        "LINKEUR": "LINK",
        "MANAEUR": "MANA",
        "MATICEUR": "MATIC",
        "SANDEUR": "SAND",
        "SOLEUR": "SOL",
        "TRXEUR": "TRX",
        "UNIEUR": "UNI",
        "XDGEUR": "DOGE",
        "XETHZEUR": "ETH",
        "XLTCZEUR": "LTC",
        "XXBTZEUR": "XBT",
        "XXLMZEUR": "XLM",
        "XXRPZEUR": "XRP"
    }

    assert pairname in kraken_pp_map, f"Pairname {pairname} not in PP lookup map!"
    return kraken_pp_map[pairname]

def fix_pairname(row):
    row["WKN"] = map_pair(row["pair"])
    return row

INPUT_FILENAME = "./testdata/trades.csv"
OUTPUT_FILENAME = "./testdata/trades_clean.csv"

with open(INPUT_FILENAME, "r") as file:
    df = pd.read_csv(INPUT_FILENAME)


df = df.apply(create_dateandtime, axis=1)
df = df.apply(fix_pairname, axis=1)
df = df.apply(calculate_value, axis=1)

df["ledgers"] = df["ledgers"].apply(lambda value: "Ref: " + value)
df["fee"] = df["fee"].apply(lambda value: "{0:.8f}".format(value))
df["vol"] = df["vol"].apply(lambda value: "{0:.8f}".format(value))

df.rename(columns={
    'type': 'Type',
    'ledgers': 'Note',
    'fee': 'Fees',
    'vol': 'Shares'
}, inplace=True)

result = df[['Date', 'Time', 'Fees', 'Shares', 'Value', 'Type', 'WKN', 'Note']].copy()

with open(OUTPUT_FILENAME, "w") as file:
    result.to_csv(file, sep=',')
