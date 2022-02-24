import pandas as pd

def create_dateandtime(row):
    row["Date"] = row["time"].split()[0]
    row["Time"] = row["time"].split()[1].split(".")[0]
    return row

def calculate_value(row):
    row["Value"] = float(row["cost"]) - float(row["fee"])
    return row

def map_pair(pairname):
    kraken_pp_map = {
        "ADAEUR": "ADA",
        "ALGOEUR": "ALGO",
        "ATOMEUR": "ATOM",
        "BCHEUR": "BCH",
        "DOTEUR": "DOT",
        "LINKEUR": "LINK",
        "MATICEUR": "MATIC",
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


with open(OUTPUT_FILENAME, "w") as file:
    df.to_csv(file)
