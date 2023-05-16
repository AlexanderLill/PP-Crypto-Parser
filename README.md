# PP-Crypto-Parser
Parser for preparing trade data from kraken for Portfolio Performance

## Input
Trade data from [kraken.com](https://kraken.com)

## Output
CSV file compatible with the CSV import of [Portfolio Performance (PP)](https://www.portfolio-performance.info/)

## Comments
- Project is a Work-in-Progress (WIP)

## Step-by-step
1. Export all `ledger` data from kraken
    1. On the kraken website, choose `History` in the top menu, then `Export`
    2. Change export to `Ledgers`, make sure that `All fields` are exported for your wanted timeframe
    3. Click on `Submit` and wait until your export is ready (refresh site)
    4. Once status is `Processed`, click on three dots on the right and choose `Download`
2. Export all history crypto rates from Portfolio Performance (PP)
    1. In PP, choose `File` - `Export` - `CSV...`
    2. Scroll to the bottom and choose `Securities` - `All historic rates` and choose storage location
3. Run `cli.py` with the following parameters (see `cli.py` for help)
    - param1
    - param2
    - param3
    - `map` can be used to specify mapping between PP Symbol and Kraken crypto currency abbreviation
4. Import the generated CSV files in Portfolio Performance
    - Import `transactions_account.csv` as account data (it includes deposits and withdrawals and costs for transfers)
    - Import `transactions_depot.csv` as transaction data (it includes buying and seeling cryptocurrencies)
    - Import `transactions_einlieferungen` as transaction data and **check the box to transform them to transfers instead of buys**
