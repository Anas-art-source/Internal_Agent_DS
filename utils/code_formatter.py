def format_code_history(code_history):
    formatted_output = ""
    for entry in code_history:
        formatted_output += "```code\n" + entry['code'] + "\n```\n"
        formatted_output += "```output\n" + entry['result'] + "\n```\n"
    return formatted_output

# Sample code history
code_history = [{'code': "import pandas as pd\n\n# Load pants data\npants_data = pd.read_csv('/home/khudi/Desktop/my_own_agent_v2/data/final_pants_dataset.csv')\n\n# Load shirts data\nshirts_data = pd.read_csv('/home/khudi/Desktop/my_own_agent_v2/data/final_shirts_dataset.csv')\n\n# Filter pants data for the year 2022\npants_data_2022 = pants_data[pants_data['Date'].str.contains('2022')]\n\n# Filter shirts data for the year 2022\nshirts_data_2022 = shirts_data[shirts_data['date'].str.contains('2022')]\n\nprint('Pants Data for the year 2022:')\nprint(pants_data_2022)\n\nprint('Shirts Data for the year 2022:')\nprint(shirts_data_2022)", 'result': 'Output before error:\n\nAn error occurred!\n    exec(code_str)\n  File "<string>", line 13, in <module>\n  File "/home/khudi/.local/lib/python3.10/site-packages/pandas/core/frame.py", line 4080, in __getitem__\n    if com.is_bool_indexer(key):\n  File "/home/khudi/.local/lib/python3.10/site-packages/pandas/core/common.py", line 136, in is_bool_indexer\n    raise ValueError(na_msg)\nValueError: Cannot mask with non-boolean array containing NA / NaN values', 'success': False}, {'code': "import pandas as pd\n\n# Load pants data\npants_data = pd.read_csv('/home/khudi/Desktop/my_own_agent_v2/data/final_pants_dataset.csv')\n\n# Load shirts data\nshirts_data = pd.read_csv('/home/khudi/Desktop/my_own_agent_v2/data/final_shirts_dataset.csv')\n\n# Check and handle missing values in Date column for pants data\npants_data['Date'] = pd.to_datetime(pants_data['Date'], errors='coerce')\npants_data = pants_data.dropna(subset=['Date'])\n\n# Check and handle missing values in date column for shirts data\nshirts_data['date'] = pd.to_datetime(shirts_data['date'], errors='coerce')\nshirts_data = shirts_data.dropna(subset=['date'])\n\n# Filter pants data for the year 2022\npants_data_2022 = pants_data[pants_data['Date'].dt.year == 2022]\n\n# Filter shirts data for the year 2022\nshirts_data_2022 = shirts_data[shirts_data['date'].dt.year == 2022]\n\nprint('Pants Data for the year 2022:')\nprint(pants_data_2022)\n\nprint('Shirts Data for the year 2022:')\nprint(shirts_data_2022)", 'result': 'Code Executed Successfully.\n\nPants Data for the year 2022:\n        Unnamed: 0  SKU ID Size   Pants Type      Fabric       Waist  ... Cuff Pattern    Store Region       Date       Sales\n0                0   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-01  513.325184\n1                1   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-02  500.999656\n2                2   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-03  516.124775\n3                3   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-04  536.161488\n4                4   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-05  522.592469\n...            ...     ...  ...          ...         ...         ...  ...  ...     ...      ...    ...        ...         ...\n642030      642030     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-27  489.490554\n642031      642031     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-28  499.019124\n642032      642032     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-29  493.201036\n642033      642033     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-30  506.401104\n642034      642034     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-31  504.900041\n\n[321200 rows x 16 columns]\nShirts Data for the year 2022:\n        Unnamed: 0   sku id                name size          color  ... price    Store Region    sales item_sold\n0                0  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_1  North  12546.0      50.0\n1                1  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_4  North  13372.0      53.0\n2                2  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_3  South  12132.0      49.0\n3                3  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_5  North  13523.0      54.0\n4                4  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_3  North  14492.0      58.0\n...            ...      ...                 ...  ...            ...  ...   ...      ...    ...      ...       ...\n570875      570875  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_2  North  13946.0      70.0\n570876      570876  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_1  South   9709.0      49.0\n570877      570877  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_1  North  13556.0      68.0\n570878      570878  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_5  North  13331.0      67.0\n570879      570879  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_5  South   9615.0      48.0\n\n[570880 rows x 18 columns]\n\n\nYou should use print(...) to see results ', 'success': True}, {'code': "import pandas as pd\n\n# Calculate total sales for pants in 2022\ntotal_pants_sales = pants_data_2022['Sales'].sum()\n\n# Calculate total sales for shirts in 2022\ntotal_shirts_sales = shirts_data_2022['sales'].sum()\n\nprint('Total Sales of Pants in 2022:', total_pants_sales)\nprint('Total Sales of Shirts in 2022:', total_shirts_sales)", 'result': 'Output before error:\nPants Data for the year 2022:\n        Unnamed: 0  SKU ID Size   Pants Type      Fabric       Waist  ... Cuff Pattern    Store Region       Date       Sales\n0                0   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-01  513.325184\n1                1   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-02  500.999656\n2                2   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-03  516.124775\n3                3   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-04  536.161488\n4                4   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-05  522.592469\n...            ...     ...  ...          ...         ...         ...  ...  ...     ...      ...    ...        ...         ...\n642030      642030     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-27  489.490554\n642031      642031     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-28  499.019124\n642032      642032     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-29  493.201036\n642033      642033     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-30  506.401104\n642034      642034     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-31  504.900041\n\n[321200 rows x 16 columns]\nShirts Data for the year 2022:\n        Unnamed: 0   sku id                name size          color  ... price    Store Region    sales item_sold\n0                0  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_1  North  12546.0      50.0\n1                1  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_4  North  13372.0      53.0\n2                2  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_3  South  12132.0      49.0\n3                3  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_5  North  13523.0      54.0\n4                4  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_3  North  14492.0      58.0\n...            ...      ...                 ...  ...            ...  ...   ...      ...    ...      ...       ...\n570875      570875  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_2  North  13946.0      70.0\n570876      570876  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_1  South   9709.0      49.0\n570877      570877  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_1  North  13556.0      68.0\n570878      570878  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_5  North  13331.0      67.0\n570879      570879  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_5  South   9615.0      48.0\n\n[570880 rows x 18 columns]\n\nAn error occurred!\n    exec(code_str)\n  File "<string>", line 4, in <module>\nNameError: name \'pants_data_2022\' is not defined', 'success': False}, {'code': "import pandas as pd\n\n# Load pants data\npants_data = pd.read_csv('/home/khudi/Desktop/my_own_agent_v2/data/final_pants_dataset.csv')\n\n# Load shirts data\nshirts_data = pd.read_csv('/home/khudi/Desktop/my_own_agent_v2/data/final_shirts_dataset.csv')\n\n# Check and handle missing values in Date column for pants data\npants_data['Date'] = pd.to_datetime(pants_data['Date'], errors='coerce')\npants_data = pants_data.dropna(subset=['Date'])\n\n# Check and handle missing values in date column for shirts data\nshirts_data['date'] = pd.to_datetime(shirts_data['date'], errors='coerce')\nshirts_data = shirts_data.dropna(subset=['date'])\n\n# Filter pants data for the year 2022\npants_data_2022 = pants_data[pants_data['Date'].dt.year == 2022]\n\n# Filter shirts data for the year 2022\nshirts_data_2022 = shirts_data[shirts_data['date'].dt.year == 2022]\n\n# Calculate total sales for pants in 2022\ntotal_pants_sales = pants_data_2022['Sales'].sum()\n\n# Calculate total sales for shirts in 2022\ntotal_shirts_sales = shirts_data_2022['sales'].sum()\n\nprint('Total Sales of Pants in 2022:', total_pants_sales)\nprint('Total Sales of Shirts in 2022:', total_shirts_sales)", 'result': 'Code Executed Successfully.\n\nPants Data for the year 2022:\n        Unnamed: 0  SKU ID Size   Pants Type      Fabric       Waist  ... Cuff Pattern    Store Region       Date       Sales\n0                0   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-01  513.325184\n1                1   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-02  500.999656\n2                2   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-03  516.124775\n3                3   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-04  536.161488\n4                4   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-05  522.592469\n...            ...     ...  ...          ...         ...         ...  ...  ...     ...      ...    ...        ...         ...\n642030      642030     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-27  489.490554\n642031      642031     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-28  499.019124\n642032      642032     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-29  493.201036\n642033      642033     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-30  506.401104\n642034      642034     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-31  504.900041\n\n[321200 rows x 16 columns]\nShirts Data for the year 2022:\n        Unnamed: 0   sku id                name size          color  ... price    Store Region    sales item_sold\n0                0  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_1  North  12546.0      50.0\n1                1  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_4  North  13372.0      53.0\n2                2  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_3  South  12132.0      49.0\n3                3  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_5  North  13523.0      54.0\n4                4  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_3  North  14492.0      58.0\n...            ...      ...                 ...  ...            ...  ...   ...      ...    ...      ...       ...\n570875      570875  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_2  North  13946.0      70.0\n570876      570876  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_1  South   9709.0      49.0\n570877      570877  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_1  North  13556.0      68.0\n570878      570878  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_5  North  13331.0      67.0\n570879      570879  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_5  South   9615.0      48.0\n\n[570880 rows x 18 columns]\nTotal Sales of Pants in 2022: 185385686.18130624\nTotal Sales of Shirts in 2022: 10537889096.0\n\n\nYou should use print(...) to see results ', 'success': True}, {'code': "import pandas as pd\n\n# Load pants data\npants_data = pd.read_csv('/home/khudi/Desktop/my_own_agent_v2/data/final_pants_dataset.csv')\n\n# Load shirts data\nshirts_data = pd.read_csv('/home/khudi/Desktop/my_own_agent_v2/data/final_shirts_dataset.csv')\n\n# Check and handle missing values in the Date column for pants data\npants_data['Date'] = pd.to_datetime(pants_data['Date'], errors='coerce')\npants_data = pants_data.dropna(subset=['Date'])\n\n# Check and handle missing values in the date column for shirts data\nshirts_data['date'] = pd.to_datetime(shirts_data['date'], errors='coerce')\nshirts_data = shirts_data.dropna(subset=['date'])\n\n# Filter pants data for the year 2022\npants_data_2022 = pants_data[pants_data['Date'].dt.year == 2022]\n\n# Filter shirts data for the year 2022\nshirts_data_2022 = shirts_data[shirts_data['date'].dt.year == 2022]\n\n# Calculate total sales for pants in 2022\ntotal_pants_sales = pants_data_2022['Sales'].sum()\n\n# Calculate total sales for shirts in 2022\ntotal_shirts_sales = shirts_data_2022['sales'].sum()\n\nprint('Total Sales of Pants in 2022:', total_pants_sales)\nprint('Total Sales of Shirts in 2022:', total_shirts_sales)", 'result': 'Code Executed Successfully.\n\nPants Data for the year 2022:\n        Unnamed: 0  SKU ID Size   Pants Type      Fabric       Waist  ... Cuff Pattern    Store Region       Date       Sales\n0                0   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-01  513.325184\n1                1   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-02  500.999656\n2                2   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-03  516.124775\n3                3   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-04  536.161488\n4                4   10046   38  Alfaiataria  Indefinido  Indefinido  ...  Não    liso  store_1  North 2022-01-05  522.592469\n...            ...     ...  ...          ...         ...         ...  ...  ...     ...      ...    ...        ...         ...\n642030      642030     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-27  489.490554\n642031      642031     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-28  499.019124\n642032      642032     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-29  493.201036\n642033      642033     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-30  506.401104\n642034      642034     695   40  Alfaiataria          Lã  Indefinido  ...  Não    Liso  store_5  South 2022-12-31  504.900041\n\n[321200 rows x 16 columns]\nShirts Data for the year 2022:\n        Unnamed: 0   sku id                name size          color  ... price    Store Region    sales item_sold\n0                0  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_1  North  12546.0      50.0\n1                1  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_4  North  13372.0      53.0\n2                2  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_3  South  12132.0      49.0\n3                3  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_5  North  13523.0      54.0\n4                4  SKU0001  Classic Cotton Tee    M  Charcoal Gray  ...   250  store_3  North  14492.0      58.0\n...            ...      ...                 ...  ...            ...  ...   ...      ...    ...      ...       ...\n570875      570875  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_2  North  13946.0      70.0\n570876      570876  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_1  South   9709.0      49.0\n570877      570877  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_1  North  13556.0      68.0\n570878      570878  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_5  North  13331.0      67.0\n570879      570879  SKU0010  Beachside Hawaiian   XL            Tea  ...   200  store_5  South   9615.0      48.0\n\n[570880 rows x 18 columns]\nTotal Sales of Pants in 2022: 185385686.18130624\nTotal Sales of Shirts in 2022: 10537889096.0\nTotal Sales of Pants in 2022: 185385686.18130624\nTotal Sales of Shirts in 2022: 10537889096.0\n\n\nYou should use print(...) to see results ', 'success': True}]
# format_code_history(code_history)s