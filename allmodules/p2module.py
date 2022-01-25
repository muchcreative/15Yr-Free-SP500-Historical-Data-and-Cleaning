#%pip install yfinance This should be downloaded in your main
import yfinance as yf
import pandas as pd
import h5py

from pathlib import Path
import json

def download_yf_tickers(tickers, period='15y'): #You can take more than 15yrs here or specifiy a start_date and end_date
  historicals = dict()
  tickers_avaliable_on_yf = []
  tickers_not_avaliable_on_yf = []

  for ticker in tickers:
    ticker_ref = yf.Ticker(ticker)
    ticker_history = ticker_ref.history(period=period, 
                                        auto_adjust=True) #auto_adjust=True, to get adjusted OHLC

    if ticker_history.empty: #Returns an empty DataFrame if the tickers YF history doesn't exist
      tickers_not_avaliable_on_yf.append(ticker)
    else: 
      historicals[ticker] = ticker_history
      tickers_avaliable_on_yf.append(ticker)
  return (historicals, tickers_avaliable_on_yf, tickers_not_avaliable_on_yf)

historicals, tickers_avaliable_on_yf, tickers_not_avaliable_on_yf = download_yf_tickers(sliced_tickers)

def record_attendance_of_tickers_to_json(tickers_to_sort, 
                                        filepath,
                                        status):
  log_filepath = f'{filepath}/{status}_yf_tickers.json'
  log_file = Path(log_filepath) #To check if the file already exists, if so we will extend and overwrtie the list
  if log_file.is_file():
    with open(log_filepath, 'r+', encoding='utf-8') as f:
      updated_tickers_lst = json.load(f)
      updated_tickers_lst.extend(tickers_to_sort)
      f.seek(0)
      json.dump(updated_tickers_lst, f, ensure_ascii=False, indent=4)
  else: #If file does not exist, we will create one and dump the tickers_lst into it
    with open(log_filepath , 'w', encoding='utf-8') as f:
      json.dump(tickers_to_sort, f, ensure_ascii=False, indent=4)
  print('{0} tickers have been logged to {0} tickers list'.format(status))
  return

def format_historicals_to_csv(historicals):
  '''
  Description:
    - Remove dividends and stock splits, as adjusted OHLC will already consider them
  Returns:
    - Formatted historicals for a CSV file
  '''
  for ticker in historicals:
    historicals[ticker] = historicals[ticker].drop(['Dividends', 'Stock Splits'], axis='columns')
    historicals[ticker] = historicals[ticker].reset_index()
  print('Finished formatting historicals as csv format')
  return historicals

def format_historicals_to_hdf5(historicals):
  '''
  Description:
    - Remove dividends and stock splits, as adjusted OHLC will already consider them
    - Change datetime to timestamps for HDF5 as HDF5 does not accept datetimes
  Returns:
    - Formatted historicals for an HDF5 file
  '''
  for ticker in historicals:
    historicals[ticker] = historicals[ticker].drop(['Dividends', 'Stock Splits'], axis='columns')
    historicals[ticker] = historicals[ticker].reset_index()
    historicals[ticker]['Date'] = historicals[ticker]['Date'].apply(lambda x: x.timestamp())
  print('Finished formatting historicals as hdf5 format')
  return historicals

def save_historicals_to_csv(historicals, filepath):
  for ticker in historicals:
    csv_filepath = f'{filepath}/{ticker}.csv'
    historicals[ticker].to_csv(csv_filepath)
    print('Ticker {} Saved as CSV'.format(ticker))
  print('All Tickers Have Been Saved')

def save_historicals_to_hdf5(historicals, filepath):
  for ticker in historicals:
    hdf5_filepath = f'{filepath}/{ticker}.hdf5'
    with h5py.File(hdf5_filepath, 'w') as f:
      history = f.create_group('historicals')
      history.create_dataset(name='15Y',
                             data=historicals[ticker],
                             maxshape=(None, 5), #Need to specify maxshape here to make extendible hdf5 files 
                             compression='gzip')
    print('Saved {} as HDF5'.format(ticker))

def check_if_tickers_were_saved_successfully(tickers_avaliable_on_yf, 
                                            filepath,
                                            save_type='hdf5'):
  assert save_type in ['csv', 'hdf5'], 'Save type must be "csv" or "hdf5"'

  tickers_not_saved = []
  for ticker in tickers_avaliable_on_yf:
    ticker_filepath = f'{filepath}/{ticker}.{save_type}'
    ticker_file = Path(ticker_filepath)
    if ticker_file.is_file():
      pass
    else:
      print("{} is missing".format(ticker))
      tickers_not_saved.append(ticker)
  return tickers_not_saved

def load_csv_tickers_as_pd_historicals(tickers, filepath):
  historicals = dict()
  '''
    Description:
      - Takes tickers as a list ['A', 'AAPL', 'AMZN']
      - Formats CSV with pandas "pd.read_csv"
    Returns:
      - Historicals dict() containing formatted pandas DataFrames with tickers as keys
  '''
  for ticker in tickers:
    csv_filepath = f'{filepath}/{ticker}.csv'
    ticker_file = Path(csv_filepath)
    if ticker_file.is_file():
      dataset = pd.read_csv(csv_filepath, index_col='Date')
      historicals[ticker] = dataset
    else:
      print('Error {} ticker is missing'.format(ticker))
  return historicals

def load_hdf5_tickers_as_pd_historicals(tickers, filepath):
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
      print('Error {} ticker is missing'.format(ticker))
    print('All Historicals Have Been Saved to Memory')
  return historicals