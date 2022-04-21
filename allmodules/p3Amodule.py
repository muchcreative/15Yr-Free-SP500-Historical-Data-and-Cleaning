'''Part 3A Tutorial Modules.

Functions:
  load_hdf5_historicals(tickers, filepath)
    Load hdf5 historicals to memory.

  collect_all_historical_lengths(historicals) 
    Collects all common historical lengths.

  find_tickers_that_match_data_length(historicals, data_len)
    Finds historical tickers that match specified data length.

  check_for_uniformity_of_dates(historicals, tickers_to_compare, comparison_ticker)
    Checks that all dates match if their lengths match.

  compile_tickers_and_missing_dates(historicals, tickers, full_date_range)
    Compiles all missing dates for the tickers.

  filter_out_the_dates_not_in_sp500(tickers_and_dates, sp500_changes)
    Filters out the dates when the tickers are not in the SP500.
  
  _collect_date_ranges_when_in_sp500(dates_mask)
    Collects all dates when the ticker was in the SP500.

  _collect_each_date_when_in_sp500(dates, date_ranges_in_sp500)
    Collects all dates for the given SP500 date ranges.

  remove_tickers_with_no_missing_dates_while_in_sp500(true_missing_tickers_and_dates)
    Removes tickers with no missing dates while in the SP500.

  collect_amount_of_missing_data_per_year(missing_tickers_and_dates)
    Collects the amount of missing data each year.

  format_missing_tickers_and_dates_for_json(full_missing_tickers_and_dates)
    Formats missing tickers and dates to save as a json. 
'''

import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

import seaborn as sns
import matplotlib.pyplot as plt

import h5py
import json
from pathlib import Path

def load_hdf5_historicals(tickers, filepath):
  '''Load hdf5 historicals to memory.

  Args:
    tickers: list containing each ticker given as a string.
    filepath: string of where the historicals are saved.

  Returns:
    historicals: dict with tickers as keys and OHLC data as values.
                 Each OHLC data is given as a pandas dataframe. 
  '''

  historicals = dict()
  columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
  
  for ticker in tickers:
    hdf5_filepath = f'{filepath}/{ticker}.hdf5'
    ticker_file = Path(hdf5_filepath)
    if ticker_file.is_file():
      with h5py.File(hdf5_filepath, 'r') as f:
        group = f['historicals']
        data = group['15Y'][()]
      dataset = pd.DataFrame(data=data, columns=columns)
      dataset['Date'] = pd.to_datetime(dataset['Date'], unit='s')  # Change the float timestamps back to datetimes.
      dataset = dataset.set_index('Date')
      historicals[ticker] = dataset
    else:
      print(f'Error {ticker} ticker is missing')
  print('All Historicals Have Been Loaded')
  return historicals

def collect_all_historical_lengths(historicals):
  '''Collects all common historical lengths.

  Counts the length of data for each ticker in the historicals.
  Same data lengths are tallied up and returned in a list.

  Args:
    historicals: dict with tickers as keys and OHLC data as values.
                 Each OHLC data is given as a pandas dataframe. 
  Returns:
    hist_len_counter: list containing tuple pairs given as
                      [(historical_length, count_of_tickers_with_length), 
                       (historical_length, count_of_tickers_with_length), ...].
  '''

  hist_len_counter = dict()

  for ticker, historical in historicals.items():
    hist_len_counter.setdefault(len(historical), 0)
    hist_len_counter[len(historical)] += 1
  return hist_len_counter

def find_tickers_that_match_data_length(historicals, data_len):
  '''Finds historical tickers that match specified data length.'''
  tickers = [ticker
             for ticker, historical in historicals.items()
             if data_len == len(historical)]
  return tickers

def check_for_uniformity_of_dates(historicals, tickers_to_compare, comparison_ticker):
  '''Checks that all dates match if their lengths match.

  Args:
    historicals: dict with tickers as keys and OHLC data as values.
                 Each OHLC data is given as a pandas dataframe. 
    tickers_to_compare: list containing each ticker given as a string.
                        They must all share the same data length.
    comparison_ticker: string of ticker to test dataset uniformity against.

  Returns:
    None
  '''

  for ticker in tickers_to_compare:
    if historicals[ticker].index.equals(historicals[comparison_ticker].index): 
      pass
    else: 
      print(f'{ticker} does not have the same dates as {comparison_ticker}')  # This will only print if the dates do not match with AAPL's dates.
  print('Comparison Completed')
  return

def compile_tickers_and_missing_dates(historicals, tickers, full_date_range):
  '''Compiles all missing dates for the tickers.

  Args:
    historicals: dict with tickers as keys and OHLC data as values.
                 Each OHLC data is given as a pandas dataframe.
    tickers: list containing each ticker given as a string.
    full_date_range: specified date range to compare each ticker's own data against.
  
  Returns:
    missing_tickers_and_dates: dict with tickers as keys and their missing dates as values.
  '''

  missing_tickers_and_dates = {ticker: full_date_range.difference(historicals[ticker].index) 
                              for ticker in tickers}
  return missing_tickers_and_dates

def filter_out_the_dates_not_in_sp500(tickers_and_dates, sp500_changes):
  '''Filters out the dates when the tickers are not in the SP500.
  
  Args:
    tickers_and_dates: dict with tickers as keys and their dates as values.
    sp500_changes: pandas dataframe containing the changes of the SP500 tickers 
                   as a list from 1996 to the present date.
  
  Returns:
    ticker_and_dates_in_sp500: dict with ticker as keys and dates as datetime values.
                               Dates have been filtered to only be when the ticker
                               is in the SP500.
  '''

  tickers_and_dates_in_sp500 = dict()

  for ticker, dates in tickers_and_dates.items():
    # Create a mask that will tell you when the ticker was in the SP500.
    mask = [True if ticker in current_sp500_tickers
            else False
            for current_sp500_tickers in sp500_changes['tickers'].values]
    
    dates_mask = sp500_changes['date'].where(mask, False)
    date_ranges_in_sp500 = _collect_date_ranges_when_in_sp500(dates_mask)  # Collect date ranges because time spent in 
                                                                           # the SP500 is continuous for a range of dates.

    dates = dates.to_series().rename()  # Pandas datetimeIndex needs to be a pandas series and renamed to use pandas series methods on it later.
    tickers_and_dates_in_sp500[ticker] = _collect_each_date_when_in_sp500(dates, date_ranges_in_sp500)
  return tickers_and_dates_in_sp500

def _collect_date_ranges_when_in_sp500(dates_mask): 
  '''Collects all dates when the ticker was in the SP500.

  Args:
    dates_mask: pseudo-bool mask for each date. The False 
                value indicates the ticker was not in the SP500 at that
                date. However, if the ticker was in the SP500 at that date,
                the value will be the date instead of a True value.

  Returns:
    date_ranges_in_sp500: list containing each date range
                          when the ticker was in the SP500.
  '''

  date_ranges_in_sp500 = []
  prev_mask = False  # Keep track of the previous mask to collect the date range at the end.

  for mask in dates_mask:  
    if mask:  # mask will be False until it hits its first date in the SP500.
      if prev_mask == False:
        start_date = mask
      end_date = mask
    else:
      if prev_mask:
        date_ranges_in_sp500.append([start_date, end_date])
    prev_mask = mask
  if prev_mask:  # Ensure that the last date range is added on the last date.
    date_ranges_in_sp500.append([start_date, end_date])
  return date_ranges_in_sp500

def _collect_each_date_when_in_sp500(dates, date_ranges_in_sp500):
  '''Collects all dates for the given SP500 date ranges.

  Args:
    dates: pandas series containing all ticker's dates as a datetime
    date_ranges_in_sp500: list containing each date range
                          when the ticker was in the SP500.
  
  Returns:
    ticker_sp500_dates: pandas series with only the dates for the
                        given date ranges.
  '''
  
  ticker_sp500_dates = None

  for date_range in date_ranges_in_sp500:
    if ticker_sp500_dates is None:
      ticker_sp500_dates = dates.loc[date_range[0]:date_range[1]]
    else:
      ticker_sp500_dates = pd.concat([ticker_sp500_dates, dates.loc[date_range[0]:date_range[1]]])
  return ticker_sp500_dates

def remove_tickers_with_no_missing_dates_while_in_sp500(true_missing_tickers_and_dates):
  '''Removes tickers with no missing dates while in the SP500.'''
  true_missing_tickers_and_dates = {ticker: missing_dates  
                                    for ticker, missing_dates in true_missing_tickers_and_dates.items()
                                    if not missing_dates.empty}
  return true_missing_tickers_and_dates

def collect_amount_of_missing_data_per_year(missing_tickers_and_dates):
  '''Collects the amount of missing data each year.

  Args:
    missing_tickers_and_dates: dict with ticker as keys and dates as 
                               datetime values.

  Returns:
    missing_occurances: pandas dataframe containing the
                        amount of missing data binned per year
    binned_years: datetimeindex per year used to bin the missing occurances
  '''

  all_dates = None
  for missing_dates in missing_tickers_and_dates.values():
    all_dates = pd.concat([all_dates, missing_dates])
  
  missing_occurances = pd.DataFrame(all_dates, columns=['Dates']).reset_index(drop=True)

  # Create bins for each year to count how much data is missing per year.
  start_date = dt.date(2007, 1, 1)
  end_date = dt.date.today() + relativedelta(years=1)
  binned_years = pd.date_range(start_date, end_date, freq='YS')
  x_axis_labels = binned_years[:-1].strftime('%Y')

  missing_occurances['Years'] = pd.cut(missing_occurances['Dates'],
                                       bins=binned_years,
                                       labels=x_axis_labels)
  return missing_occurances, binned_years

def format_missing_tickers_and_dates_for_json(full_missing_tickers_and_dates):
  '''Formats missing tickers and dates to save as a json. 

  Changes datetime values to float timestamps in order to save them as a json.

  Args:
    full_missing_tickers_and_dates: dict with ticker as keys and dates as 
                                    datetime values.

  Returns:
    formatted_missing_tickers_and_dates: dict with ticker as keys and dates as 
                                         float timestamp values.
  '''

  formatted_missing_tickers_and_dates = dict()

  for ticker, missing_dates in full_missing_tickers_and_dates.items():
    # Need to convert datetimes to timestamps and a list to save file as a json.
    formatted_missing_tickers_and_dates[ticker] = missing_dates.apply(lambda x: x.timestamp()).values.tolist() 
  return formatted_missing_tickers_and_dates