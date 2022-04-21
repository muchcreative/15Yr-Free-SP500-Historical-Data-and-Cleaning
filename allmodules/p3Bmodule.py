'''Part 3B Tutorial Modules.

Functions:
  generate_iex_historical_batch_urls(tickers, date_length, partition_size=50, IEX_TOKEN=IEX_TOKEN)
    Generates historical batch urls for IEX Cloud.

  partition(tickers, partition_size)
    Partitions tickers into a list of lists with specified partition size.

  collect_tickers_not_found_on_iex(historicals, ticker_batches)
    Collects tickers that were not avaliable on IEX Cloud.

  add_missing_iex_tickers_to_historicals(historicals, missing_iex_tickers)
    Adds missing IEX tickers to historicals as empty lists.

  collect_data_that_is_still_missing(historicals, yf_missing_tickers_and_dates)
    Collects the tickers and dates that are still missing after the IEX download and YF download.

  convert_timestamps_to_datetimes(data_still_missing)
    Converts timestamps to datetimes.

  calculate_metrics_of_added_data_from_iex(historicals, data_still_missing, yf_missing_tickers_and_dates)
    Calculates updated missing data metrics with the addition of the IEX data.

  check_remaining_missing_tickers(data_still_missing)
    Checks which tickers are still missing from the database.
  
  format_data_still_missing_for_json(data_still_missing)
    Formats data that is still missing to a json format.

  merge_historicals(yf_historicals, iex_historicals)
    Merges given historicals.

  test_for_ordinance(historicals)
    Tests that historicals are all in chronological order.
'''

import numpy as np
import pandas as pd
import datetime as dt
from itertools import chain

import requests

from p3Binputs.apitokens import IEX_TOKEN 

def generate_iex_historical_batch_urls(tickers, date_length, partition_size=50, IEX_TOKEN=IEX_TOKEN):
  '''Generates historical batch urls for IEX Cloud.
  
  Args:
    tickers: list of tickers as strings.
    date_length: string specifying how much data will be downloaded
    partition_size: integer specifying how many tickers will be downloaded
                    in each batch url. Max is 100 for IEX Cloud. Defaults 50.
    IEX_TOKEN: string of your IEX TOKEN. Defaults to the imported IEX Token
  
  Returns:
    historical_batch_urls: list of historical batch urls with specified partition_size
    ticker_batches: list of lists with each list denoting the tickers in each 
                    generated batch url. Indices match the historical_batch_urls indices.
  '''

  historical_batch_urls = []
  ticker_batches = []

  for ticker_partition in partition(tickers, partition_size):
    ticker_batches.append(ticker_partition)
    ticker_partition = ",".join(ticker_partition)
    # The batch url should be changed to the respective sandbox mode url if you want to test if it works first.
    batch_url = (f"https://cloud.iexapis.com/stable/stock/market/batch?symbols="
                + f"{ticker_partition}&types=chart&range={date_length}&token={IEX_TOKEN}")
    historical_batch_urls.append(batch_url)
  return historical_batch_urls, ticker_batches

def partition(tickers, partition_size):
  '''Partitions tickers into a list of lists with specified partition size.'''
  partitioned_tickers = []
  for i in range(0, len(tickers), partition_size):
    partitioned_tickers.append(tickers[i:i+partition_size])
  return partitioned_tickers

def download_iex_historicals(batch_urls):
  '''Downloads IEX historicals by making API requests to IEX Cloud.

  Downloaded data is for the adjusted Open, High, Low, Close and Volume.
  If no server response from IEX Cloud is recieved when the batch url requests
  the data, the function will safely raise a SystemExit. A key error will be 
  logged if the ticker data for a date is missing.
  
  Args:
    batch_urls: list of IEX batch urls.

  Returns:
    historicals: dict with tickers as keys and OHLC data as list of lists.
                 Each list contains a date as a timestamp and the adjusted OHLCV data
                 for that date.
    key_error_log: list of lists of the key errors that occured. Each list contains
                   which ticker that caused the key error and the date that it happened. 

  Raises:
    RequestException: SystemExit, prints "Stopped at batch url: {batch_url}" and "Status Code: {hist_response.status_code}".
    KeyError: Excepted, logs error into key_error_log.
  '''

  historicals = dict()
  key_error_log = []

  for batch_url in batch_urls:
    try:
      hist_response = requests.get(batch_url)
      hist_response.raise_for_status()
      hist_response = hist_response.json()
    except requests.exceptions.RequestException as e:
      print(f'Stopped at batch url: {batch_url}')
      print(f'Status Code: {hist_response.status_code}')
      raise SystemExit(e)
    for ticker in hist_response:
      ticker_hist = list()
      total_amount_of_days = len(hist_response[ticker]['chart'])
      for day in range(0, total_amount_of_days):
        current_date = hist_response[ticker]['chart'][day]['date']
        current_timestamp = dt.datetime.strptime(current_date,"%Y-%m-%d").timestamp()  # Change string date to timestamp to save as in hdf5 format.
        try:
          ticker_hist.append([current_timestamp,
                              hist_response[ticker]['chart'][day]['fOpen'],  # As per IEX Cloud documentation the 'f' in front of
                              hist_response[ticker]['chart'][day]['fHigh'],  # the OHLCV names specify for the adjusted OHLCV values.
                              hist_response[ticker]['chart'][day]['fLow'],
                              hist_response[ticker]['chart'][day]['fClose'],
                              hist_response[ticker]['chart'][day]['fVolume']])
          historicals[ticker] = ticker_hist
        except KeyError as e:
          print(f"Key Error with {current_date} at {ticker} for {e}")
          key_error_log.append([ticker, current_date, e])
      print(f'Finished downloading {ticker}')
  return historicals, key_error_log

def collect_tickers_not_found_on_iex(historicals, ticker_batches):
  '''Collects tickers that were not avaliable on IEX Cloud.

  There are two ways that the tickers are not found on IEX. The first 
  is that the ticker is missing from the historicals dict.The second is 
  that the historicals  dict has the ticker key but is paired with an empty 
  array. Both ways will be checked for and returned.  

  Args:
    historicals: dict with tickers as keys and OHLC data as a list of lists.
    ticker_batches: list of lists with each list denoting the tickers in each 
                    generated batch url.

  Returns:
    missing_iex_tickers: list of tickers that are missing from the historical dict
    empty_historical_tickers: list of tickers that are present in the historical dict,
                              but are paired as empty arrays.
  '''

  flat_ticker_batches = chain.from_iterable(ticker_batches)  # Flatten the list of lists.
  
  # Check if the ticker keys are missing.
  missing_iex_tickers = [ticker 
                         for ticker in flat_ticker_batches
                         if ticker not in list(historicals.keys())]  
  
  # Check if the ticker keys are paired with empty arrays.
  empty_historical_tickers =  [ticker
                              for ticker, historicals in historicals.items()
                              if not historicals]
  return missing_iex_tickers, empty_historical_tickers

def add_missing_iex_tickers_to_historicals(historicals, missing_iex_tickers):
  '''Adds missing IEX tickers to historicals as empty lists.'''
  for ticker in missing_iex_tickers:
    historicals[ticker] = []
  return historicals

def collect_data_that_is_still_missing(historicals, yf_missing_tickers_and_dates):
  '''Collects the tickers and dates that are still missing after the IEX download and YF download.'''
  data_still_missing = {ticker: np.setdiff1d(yf_missing_tickers_and_dates[ticker], historicals[ticker])
                       for ticker in historicals}
  return data_still_missing

def convert_timestamps_to_datetimes(data_still_missing):
  '''Converts timestamps to datetimes.'''
  data_still_missing = {ticker:
                               [dt.date.fromtimestamp(missing_date)
                               for missing_date in missing_dates]
                       for ticker, missing_dates in data_still_missing.items()}
  return data_still_missing

def calculate_metrics_of_added_data_from_iex(historicals, data_still_missing, yf_missing_tickers_and_dates):
  '''Calculates updated metrics with the addition of new data.
  
  Args:
    historicals: dict with tickers as keys and OHLC data as a list of lists.
    data_still_missing: dict with tickers as keys and their 
                        current missing dates as values after IEX data addition.
    yf_missing_tickers_and_dates: dict with tickers as keys and their missing
                                  datas as values before IEX data addition.

  Returns:
    tickers_and_amount_missing: dict with tickers as keys and integer values specifying
                                how much data is still missing for the ticker.
    total_dates_missing: integer as the total amount of data still missing.
    tickers_and_amount_reduced: dict with tickers as keys and integer values specifying
                               how much data was reduced by adding the IEX data. 
    total_reductions: integer as the amount of missing data that has been 
                      reduced by the IEX data.
  '''

  tickers_and_amount_missing = {ticker: len(data_still_missing[ticker])
                              for ticker in historicals}
  total_dates_missing = sum(tickers_and_amount_missing.values())

  tickers_and_amount_reduced = {ticker: len(yf_missing_tickers_and_dates[ticker]) - len(data_still_missing[ticker])
                              for ticker in historicals}
  total_reductions = sum(tickers_and_amount_reduced.values())
  return (tickers_and_amount_missing, total_dates_missing, tickers_and_amount_reduced, total_reductions)

def check_remaining_missing_tickers(data_still_missing):
  '''Checks which tickers are still missing from the database.
  
  Args:
    data_still_missing: dict with tickers as keys and their 
                        current missing dates as values after IEX data addition.
  
  Returns:
    remaining_missing_tickers: list
    filled_tickers: list
  '''

  remaining_missing_tickers = []
  filled_tickers = []

  for ticker, dates in data_still_missing.items():
    if dates.size == 0:
      filled_tickers.append(ticker)
    else:
       remaining_missing_tickers.append(ticker)
  return remaining_missing_tickers, filled_tickers

def format_data_still_missing_for_json(data_still_missing):
  '''Formats data that is still missing to a json format.'''
  formatted_data_still_missing = dict()

  # Remove filled tickers as they are empty here (not missing anymore).
  for ticker in filled_tickers:
    data_still_missing.pop(ticker)

  # Need ndarray as a list for json file saving.
  for ticker, missing_dates in data_still_missing.items():
    formatted_data_still_missing[ticker] = missing_dates.tolist()
  return  formatted_data_still_missing

def merge_historicals(yf_historicals, iex_historicals):
  '''Merges given historicals.

  Historicals are concated with each other and same or overlapping dates 
  are removed. The merged dataframe is then sorted by ascending dates 
  from past to present.
  
  Args:
    yf_historicals: dict with tickers as keys and OHLC data as values.
                    Each OHLC data is given as a pandas dataframe. 
    iex_historicals: dict with tickers as keys and OHLC data as values.
                     Each OHLC data is given as a pandas dataframe. 
  
  Returns:
    merged_historicals: dict with tickers as keys and OHLC data as a pandas dataframe.
  '''

  merged_historicals = dict()

  all_tickers = set(yf_historicals.keys()) + set(iex_historicals.keys())
  for ticker in all_tickers:
    merged_historicals[ticker] = pd.concat([yf_historicals[ticker], iex_historicals[ticker]])
    merged_historicals[ticker] = merged_historicals[ticker].groupby(merged_historicals[ticker].index).first().sort_index()
  return merged_historicals

def test_for_ordinance(historicals):
  '''Tests that historicals are all in chronological order.

  Args:
    historicals: dict with tickers as keys and OHLC data as values.
                 Each OHLC data is given as a pandas dataframe. 

  Returns:
    ordinance: bool. Will be True if all the data is in chronological order
               or False if the data is not in chronological order
  '''

  ordinance = True
  for ticker in historicals:
    current_date = dt.date.min
    for date in historicals[ticker].index:
      if current_date > date or current_date == date:
        print(f'Error with ticker {ticker} on {date}')
        ordinance = False
        return ordinance
      else:
        current_date = date
  return ordinance