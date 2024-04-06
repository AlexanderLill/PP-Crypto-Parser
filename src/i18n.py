import os
from pathlib import Path

class I18n:

    CSV_DEPOT_COLUMNS = [
        'CSVColumn_Date',
        'CSVColumn_Time',
        'CSVColumn_Type',
        'LabelSecurity',
        'CSVColumn_Shares',
        'CSVColumn_Quote',
        'ColumnAmount',
        'CSVColumn_Fees',
        'CSVColumn_Taxes',
        'ColumnNetValue',
        'CSVColumn_AccountName',
        'CSVColumn_AccountName2nd',
        'CSVColumn_Note',
        'ColumnSource'
    ]

    CSV_ACCOUNT_COLUMNS = [
        'CSVColumn_Date',
        'CSVColumn_Time',
        'CSVColumn_Type',
        'ColumnAmount',
        'Balance',
        'ColumnSecurity',
        'CSVColumn_Shares',
        'ColumnPerShare',
        'CSVColumn_AccountName2nd',
        'CSVColumn_Note',
        'ColumnSource'
    ]

    def __init__(self, language):
        self._res_dir = self._determine_resource_dir()
        print(f"Loading translations from: {self._res_dir}")

        self._constants = self._load_language(language)

        self._constants['DEPOT_COLUMNS'] = self._translate_array(self.CSV_DEPOT_COLUMNS)
        self._constants['ACCOUNT_COLUMNS'] = self._translate_array(self.CSV_ACCOUNT_COLUMNS)

    def _determine_resource_dir(self):
        proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return proj_dir / Path("resources/portfolio")

    def get(self, key):
        if key in self._constants:
            return self._constants[key]
        else:
            print(f"Error: Could not find key: {key}")
            return self._constants.get(key, key)

    def _load_language(self, language):
        result = {}

        if language == "en":
            language = ""
        else:
            language = f"_{language}"

        files = [
            Path(f"name.abuchen.portfolio/src/name/abuchen/portfolio/model/labels{language}.properties"),
            Path(f"name.abuchen.portfolio/src/name/abuchen/portfolio/messages{language}.properties"),
            Path(f"name.abuchen.portfolio.ui/src/name/abuchen/portfolio/ui/messages{language}.properties"),
        ]
        for file in files:
            full_file_name = Path(self._res_dir) / file
            result.update(self._load_from_file(full_file_name))
        
        return result

    def _load_from_file(self, filename):
        result = {}
        try:
            with open(filename, encoding='utf-8') as f:
                rows = f.readlines()
                for row in rows:
                    if row.strip() and not row.startswith("#"):
                        row = row.encode('utf-8').decode('unicode-escape')
                        items = row.split(" = ")
                        key = items[0]
                        value = "".join(items[1:])
                        result[key.strip()] = value.strip()
        except Exception as e:
            print(f"Error loading file {filename}: {e}")
        return result

    def _translate_array(self, array):
        result = []
        for item in array:
            result.append(self.get(item))
        return result
