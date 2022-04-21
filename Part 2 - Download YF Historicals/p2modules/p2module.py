'''Part 2 Tutorial Modules.

Functions:
  download_yf_tickers(tickers, start_date='2007-01-22', end_date='2022-01-19')
    Downloads specified ticker data from Yahoo Finance.

  log_availability_of_tickers_to_json(tickers, filepath, status)
    Saves which tickers were or were not avaliable on yahoo finance as a json file.

  format_historicals_to_save_as_csv(historicals)
    Formats historicals to safely save as csv files.

  format_historicals_to_save_as_hdf5(historicals)
    Formats historicals to safely save as hdf5 files.

  save_historicals_to_csv(historicals, filepath)
    Save historicals as csv files.

  save_historicals_to_hdf5(historicals, filepath)
    Saves historicals as hdf5 files.

  check_if_tickers_were_saved_successfully(tickers, filepath, save_type='hdf5')
    Checks if the tickers were saved successfully as their specified save type.

  load_csv_historicals(tickers, filepath)
    Load csv historicals to memory.

  load_hdf5_historicals(tickers, filepath)
    Load hdf5 historicals to memory.
'''

import yfinance as yf  # You will need to run %pip install yfinance in your main.
import pandas as pd
import h5py

from pathlib import Path
import json

def download_yf_tickers(tickers, start_date='2007-01-22', end_date='2022-01-19'):
  '''Downloads specified ticker data from Yahoo Finance.

  Uses the yahoo finance module to downloaded the specified tickers' adjusted OHLC data
  for the given start and end date range. Along with the downloaded data,
  two lists are returned. If the ticker was not avaliable for download
  on yahoo finance or were not avaliable for the given date range, the returned
  lists will record which tickers were or were not avaliable from yahoo finance.

  Args:
    tickers: list containing each ticker given as a string.
    start_date: str with format as 'year-month-day'. Defaults '2007-01-22'.
    end_date: str with format as 'year-month-day'. Defaults '2022-01-19'.

  Returns:
    historicals: dict with tickers as keys and the adjusted OHLCV data as values.
                 Each OHLCV data is given as a pandas dataframe. 
    tickers_avaliable_on_yf: list of tickers that were avaliable on yahooo finance.
    tickers_not_avaliable_on_yf: list of tickers that were not avaliable on yahoo finance.
  '''

  historicals = dict()
  tickers_avaliable_on_yf = []
  tickers_not_avaliable_on_yf = []

  for ticker in tickers:
    ticker_ref = yf.Ticker(ticker)
    ticker_history = ticker_ref.history(start_date=start_date, end_date=end_date, auto_adjust=True)  # Set auto_adjust=True to get the adjusted OHLC data.

    if ticker_history.empty:  # Returns an empty DataFrame if the tickers Yahoo Finance history does not exist.
      tickers_not_avaliable_on_yf.append(ticker)
    else: 
      historicals[ticker] = ticker_history
      tickers_avaliable_on_yf.append(ticker)
  return (historicals, tickers_avaliable_on_yf, tickers_not_avaliable_on_yf)

def log_availability_of_tickers_to_json(tickers, filepath, status):
  '''Saves which tickers were or were not avaliable on yahoo finance as a json file.

  If the json file already exists because you are downloading data from multiple
  sources the tickers will be added to the json file if they don't already exist
  in the file.
  
  Args:
    tickers: list containing each ticker given as string.
    filepath: string of where to save the attendance log to.
    status: string of the status of the tickers if they were available or missing
            from yahoo finance. The status will determine the name to give to the
            json file. Typically used statuses are {'avaliable', 'missing'}.

  Returns:
    None
  '''

  log_filepath = f'{filepath}/{status}_yf_tickers.json'
  log_file = Path(log_filepath)  # Check if the file already exists, if so we will add the tickers to this list.
  if log_file.is_file():
    with open(log_filepath, 'r+', encoding='utf-8') as f:
      previous_tickers = json.load(f)
      previous_tickers.extend(tickers)
      updated_tickers = sorted(set(previous_tickers))
      f.seek(0)
      json.dump(updated_tickers, f, ensure_ascii=False, indent=4)
  else:  # If the file does not exist, we will create one and dump the tickers list into it.
    with open(log_filepath , 'w', encoding='utf-8') as f:
      json.dump(tickers, f, ensure_ascii=False, indent=4)
  print(f'{status} tickers have been logged to {status} tickers list')
  return

def format_historicals_to_save_as_csv(historicals):
  '''Formats historicals to safely save as csv files.

  Args:
    historicals: dict with tickers as keys and OHLC data as values.
                 Each OHLC data is given as a pandas dataframe. 

  Returns:
    csv_historicals: formatted historicals to save as csv files
  '''

  csv_historicals = {}

  for ticker in historicals:
    csv_historicals[ticker] = historicals[ticker].drop(['Dividends', 'Stock Splits'], axis='columns')
    csv_historicals[ticker] = csv_historicals[ticker].reset_index()
  print('Finished formatting historicals as csv format')
  return csv_historicals

def format_historicals_to_save_as_hdf5(historicals):
  '''Formats historicals to safely save as hdf5 files.

  Args:
    historicals: dict with tickers as keys and OHLC data as values.
                 Each OHLC data is given as a pandas dataframe. 

  Returns:
    historicals: formatted historicals to save as hdf5 files
  '''

  hdf5_historicals = {}

  for ticker in historicals:
    hdf5_historicals[ticker] = historicals[ticker].drop(['Dividends', 'Stock Splits'], axis='columns')
    hdf5_historicals[ticker] = hdf5_historicals[ticker].reset_index()
    hdf5_historicals[ticker]['Date'] = hdf5_historicals[ticker]['Date'].apply(lambda x: x.timestamp())
  print('Finished formatting historicals as hdf5 format')
  return hdf5_historicals

def save_historicals_to_csv(historicals, filepath):
  '''Save historicals as csv files.'''
  for ticker in historicals:
    csv_filepath = f'{filepath}/{ticker}.csv'
    historicals[ticker].to_csv(csv_filepath)
    print(f'Ticker {ticker} Saved as CSV')
  print('All Tickers Have Been Saved')

def save_historicals_to_hdf5(historicals, filepath):
  '''Saves historicals as hdf5 files.'''
  for ticker in historicals:
    hdf5_filepath = f'{filepath}/{ticker}.hdf5'
    with h5py.File(hdf5_filepath, 'w') as f:
      history = f.create_group('historicals')
      history.create_dataset(name='15Y',
                             data=historicals[ticker],
                             maxshape=(None, 6),  # Specify a maxshape of None in the row axis so future dates can be added on the rows.
                             compression='gzip')
    print(f'Saved {ticker} as HDF5')
  print('All Tickers Have Been Saved')

def check_if_tickers_were_saved_successfully(tickers, filepath, save_type='hdf5'):
  '''Checks if the tickers were saved successfully as their specified save type.

  Args:
    tickers: list containing each ticker given as a string.
    filepath: string of where the historicals are saved.
    save_type: string that checks if the tickers were saved in the
               specifed type. Options are {'hdf5', 'csv'}.
               Defaults to 'hdf5'.

  Returns:
    tickers_not_saved: list containing the tickers
                       that were not saved successfully.

  Raises:
    AssertionError: Save type must be "csv" or "hdf5"
  '''

  assert save_type in ['csv', 'hdf5'], 'Save type must be "csv" or "hdf5"'

  tickers_not_saved = []

  for ticker in tickers:
    ticker_filepath = f'{filepath}/{ticker}.{save_type}'
    ticker_file = Path(ticker_filepath)
    if ticker_file.is_file():
      pass
    else:
      print(f"{ticker} is missing")
      tickers_not_saved.append(ticker)
  return tickers_not_saved

def load_csv_historicals(tickers, filepath):
  '''Load csv historicals to memory.

  Args:
    tickers: list containing each ticker given as a string.
    filepath: string of where the historicals are saved.

  Returns:
    historicals: dict with tickers as keys and OHLC data as values.
                 Each OHLC data is given as a pandas dataframe. 
  '''

  historicals = dict()
  
  for ticker in tickers:
    csv_filepath = f'{filepath}/{ticker}.csv'
    ticker_file = Path(csv_filepath)
    if ticker_file.is_file():
      dataset = pd.read_csv(csv_filepath, index_col='Date')
      historicals[ticker] = dataset
    else:
      print(f'Error {ticker} ticker is missing')
  return historicals

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
      dataset['Date'] = pd.to_datetime(dataset['Date'], unit='s')
      dataset = dataset.set_index('Date')
      historicals[ticker] = dataset
    else:
      print(f'Error {ticker} ticker is missing')
    print('All Historicals Have Been Saved to Memory')
  return historicals