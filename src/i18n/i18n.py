import os
i18n_dir = os.path.dirname(os.path.abspath(__file__))

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
        self._constants = self.load_language(language)

        self._constants['DEPOT_COLUMNS'] = self.translate_array(self.CSV_DEPOT_COLUMNS)
        self._constants['ACCOUNT_COLUMNS'] = self.translate_array(self.CSV_ACCOUNT_COLUMNS)

        print(f"Folder for translation files: {i18n_dir}")

    def get(self, key):
        return self._constants.get(key, key)

    def load_language(self, language):
        result = {}

        files = [
            os.path.join(i18n_dir, f"labels_{language}.properties"),
            os.path.join(i18n_dir, f"messages_{language}.properties"),
            os.path.join(i18n_dir, f"extra_{language}.properties"),  # TODO: Avoid manual prep for `extra` file.
        ]
        for f in files:
            result.update(self.load_from_file(f))
        
        return result

    def load_from_file(self, filename):
        result = {}
        try:
            with open(filename, encoding='utf-8') as f:
                rows = f.readlines()
                for row in rows:
                    if row.strip() and not row.startswith("#"):
                        row = row.encode('utf-8').decode('unicode-escape')
                        key, value = row.split(" = ")
                        result[key.strip()] = value.strip()
        except Exception as e:
            print(f"Error loading file {filename}: {e}")
        return result

    def translate_array(self, array):
        result = []
        for item in array:
            result.append(self.get(item))
        return result
