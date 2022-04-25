'''Part 1 Tutorial Modules.

Module used for the GitHub repository "Part 1 - Collect Past SP500 Constituents."
This module contains the functions required to aggregate all the previous sp500 constituents
up until the present year.

Functions:
  get_sp500_constituents_records(filepath)
    Gets SP500 constituents records from the specified filepath.

  format_sp500_constituents_records(df)
    Formats sp500 constituents records by splitting up individual tickers and changing date strings to datetimes.

  slice_sp500_constituents_records(df, start_date, end_date)
    Slices sp500 constituents records to specified start and end dates.

  collect_all_sp500_constituents(df)
    Returns an alphabetically sorted list of all constituents that were in the sp500.
'''

import pandas as pd
import datetime as dt

from pathlib import Path

def get_sp500_constituents_records(filepath):
  '''Gets SP500 constituents records from the specified filepath.

  Args:
    filepath: string of where the sp500 constituents records is saved.
      
  Returns:
    sp500_constituents_records: pandas dataframe. If the filepath does not point 
                                to the file location; None will be returned.
  '''

  sp500_constituents_file = Path(filepath)
  if sp500_constituents_file.is_file():
    sp500_constituents_records = pd.read_csv(filepath, index_col='date')
    return sp500_constituents_records
  else:
    print('Could not find SP500 Constituents Records')
  return

def format_sp500_constituents_records(df):
  '''Formats sp500 constituents records by splitting up individual tickers and changing date strings to datetimes.'''
  df['tickers'] = df['tickers'].apply(lambda x: sorted(x.split(',')))  # Change each ticker row to lists.
  df.index = pd.to_datetime(df.index, format = '%Y-%m-%d')  # Change date (str) index to a datetime index.
  return df

def slice_sp500_constituents_records(df, start_date, end_date):
  '''Slices sp500 constituents records to specified start and end dates.'''
  start_date = dt.datetime.strptime(start_date, '%Y-%m-%d')  # Change string dates to datetime for pandas to compare them.
  end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
  date_ranged_df = df.loc[start_date:end_date]
  return date_ranged_df

def collect_all_sp500_constituents(df):
  '''Returns an alphabetically sorted list of all constituents that were in the sp500.'''
  sp500_constituents = set()
  for years_constituents in df['tickers']:
    sp500_constituents = sp500_constituents | set(years_constituents)
  return sorted(sp500_constituents)