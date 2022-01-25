import pandas as pd
import datetime as dt

from pathlib import Path
import json

def get_sp500_constitutents_records(filepath):
    sp500_constituents_file = Path(filepath)
    if sp500_constituents_file.is_file():
      df = pd.read_csv(filepath, index_col='date')
    else:
      return print('Could not find SP500 Constituents Records')

def format_sp500_constituents_records(df):
  df['tickers'] = df['tickers'].apply(lambda x: sorted(x.split(','))) #Change each ticker row to lists
  df.index = pd.to_datetime(df.index, format = '%Y-%m-%d') #Change Date (str) Index to a Datetime Index
  return df

def slice_sp500_constituents_records(df,
                                     start_date,
                                     end_date):
  start_date = dt.datetime.strptime(start_date,'%Y-%m-%d') #Change string dates to datetime for pandas to compare them
  end_date = dt.datetime.strptime(end_date,'%Y-%m-%d')
  date_ranged_df = df.loc[start_date:end_date]
  return date_ranged_df

def collect_all_sp500_constituents(df):
  '''Returns an alphabetically sorted list of all constituents that were in the sp500 for the sliced date_range df'''
  sp500_constituents = set()
  for years_constituents in df['tickers']:
    sp500_constituents = sp500_constituents | set(years_constituents)
  return sorted(sp500_constituents)