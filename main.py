import numpy as np
import pandas as pd
import math
from scipy import stats
import xlsxwriter
import requests

stocks = pd.read_csv('ressources/sp_500_stocks.csv')

from mysecrets import IEX_CLOUD_API_TOKEN

# Dividing stocks into groups
def chuncks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

symbol_groups = list(chuncks(stocks['Ticker'], 100))
symbol_strings = []

# initializing the final dataframe to return
my_columns = ['Ticker', 'Stock Price', 'One-Year Price Return', 'Number of Shares to Buy']
final_df = pd.DataFrame(columns = my_columns)

# Making batch API calls to get stocks data
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))

for symbol_str in symbol_strings:
    batch_api_call_url = f'https://sandbox.iex.cloud/v1/data/core/advanced_stats,quote/{symbol_str}?token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    splitted_symbols = symbol_str.split(',')
    # Appending each stock's data to final_df
    for i in range (0, len(splitted_symbols)):
        final_df.loc[-1] =  [splitted_symbols[i], data[i+len(splitted_symbols)]['latestPrice'], data[i]['year1ChangePercent'], 'N/A']
        final_df.index = final_df.index + 1  # shifting index
        final_df = final_df.sort_index()  # sorting by index
        index = final_df.index

# Sorting by one-year return and picking the 50 best-performing stocks
final_df.sort_values('One-Year Price Return', ascending=False, inplace=True)
final_df = final_df[:50]
final_df.reset_index(inplace=True)

# Getting user's portfolio size
def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the size of your portfolio: ")
    try:
        float(portfolio_size)
    except ValueError:
        print("That is not a number, Please try again.")
        portfolio_size = input("Enter the size of your portfolio: ")

portfolio_input()
position_size = float(portfolio_size)/len(final_df.index)

# Computing how much of each stock should the user buy
for i in range (0, len(final_df)):
    final_df.loc[i, 'Number of Shares to Buy'] = math.floor(position_size/final_df.loc[i, 'Stock Price'])

# Droping unnecessary columns
final_df.drop(['index'], axis=1, inplace=True)

# Saving trades on an excel sheet
writer = pd.ExcelWriter('recommended trades.xlsx', engine = 'xlsxwriter')
final_df.to_excel(writer, "Recommended Trades", index = False)

# Formatting the sheet
bg_color = '#0a0a23'
font_color = "#ffffff"

string_format = writer.book.add_format(
    {
        'font_color': font_color,
        'bg_color': bg_color,
        'border': 1
    }
)

dollar_format = writer.book.add_format(
    {
        'num_format': '$0.00',
        'font_color': font_color,
        'bg_color': bg_color,
        'border': 1
    }
)

integer_format = writer.book.add_format(
    {
        'num_format': 0,
        'font_color': font_color,
        'bg_color': bg_color,
        'border': 1
    }
)

percent_format = writer.book.add_format(
    {
        'num_format': '00.00%',
        'font_color': font_color,
        'bg_color': bg_color,
        'border': 1
    }
)

column_formats = { 
                    'A': ['Ticker', string_format],
                    'B': ['Stock Price', dollar_format],
                    'C': ['One-Year Price Return', percent_format],
                    'D': ['Number of Shares to Buy', integer_format]
                    }

for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)

writer._save()