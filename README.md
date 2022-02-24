# PP-Crypto-Parser
Parser for preparing trade data from kraken for Portfolio Performance

## Input
Trade data from [kraken.com](https://kraken.com)

## Output
CSV file compatible with the CSV import of [Portfolio Performance (PP)](https://www.portfolio-performance.info/)

## Comments
- Project is a Work-in-Progress (WIP)
- The `kraken_pp_map` contains the mapping from kraken currency pair names to the WKN that will be used in Portfolio Performance. It can be removed if you use the same names in both kraken and PP.
