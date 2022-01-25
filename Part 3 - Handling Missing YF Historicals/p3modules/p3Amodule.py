import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

import seaborn as sns
import matplotlib.pyplot as plt

import h5py
import json
from pathlib import Path

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
      dataset['Date'] = pd.to_datetime(dataset['Date'], unit='s') #Change our timestamps back to datetimes
      dataset = dataset.set_index('Date')
      historicals[ticker] = dataset
    else:
      print('Error {} ticker is missing'.format(ticker))
  print('All Historicals Have Been Loaded')
  return historicals

def count_all_historicals_lengths(historicals):
  hist_len_counter = dict()
  for ticker, historical in historicals.items():
    hist_len_counter.setdefault(len(historical), 0)
    hist_len_counter[len(historical)] += 1
  return hist_len_counter

def look_for_target_historicals_lengths(historicals, target_len):
  target_len_tickers = [ticker
                        for ticker, historical in historicals.items()
                        if target_len == len(historical)]
  return target_len_tickers

def check_for_uniformity_of_dates(historicals, 
                                  tickers_to_compare, 
                                  comparsion_ticker):
  for ticker in tickers_to_compare:
    if historicals[ticker].index.equals(historicals[comparison_ticker].index): 
      pass
    else: 
      print('{} does not have the same dates as {}'.format(ticker, comparison_ticker)) #This will print only if dates do not match with AAPL
  print('Comparison Completed')

def compile_all_missing_dates(historicals,
                              tickers_with_missing_dates,
                              full_date_range):
  missing_tickers_and_dates = {ticker: full_date_range.difference(historicals[ticker].index) 
                              for ticker in tickers_with_missing_dates}
  return missing_tickers_and_dates

def filter_out_when_dates_not_in_sp500(missing_tickers_and_dates, sp500_changes):
  true_missing_tickers_and_dates = dict()
  for ticker, missing_dates in missing_tickers_and_dates.items():
    #Create a mask that will tell you when the ticker was in the SP500
    mask = [True if ticker in current_sp500_tickers
            else False
            for current_sp500_tickers in sp500_changes['tickers'].values]
    
    dates_mask = sp500_changes['date'].where(mask, False)
    times_in_sp500 = _get_all_times_in_sp500(dates_mask)

    #Compare when it was in the sp500 to what data is missing from your historicals
    missing_dates = missing_dates.to_series().rename() #DatetimeIndex needs to be series to use pd.series.loc[] function
    true_missing_tickers_and_dates[ticker] = _get_missing_dates_when_in_sp500(ticker,
                                                                              missing_dates, 
                                                                              times_in_sp500)
  true_missing_tickers_and_dates = _remove_tickers_with_no_missing_dates_while_in_sp500(true_missing_tickers_and_dates)
  return true_missing_tickers_and_dates

def _get_all_times_in_sp500(dates_mask): 
  times_in_sp500 = []
  last_mask = False
  for mask in dates_mask:  
    if mask:
      if last_mask == False:
        start_date = mask
      end_date = mask
    else:
      if last_mask:
        times_in_sp500.append([start_date, end_date])
    last_mask = mask
  if last_mask:
    times_in_sp500.append([start_date, end_date])
  return times_in_sp500

def _get_missing_dates_when_in_sp500(ticker,
                                     missing_dates, 
                                     times_in_sp500):
  ticker_true_missing_dates = None
  for time in times_in_sp500:
    if ticker_true_missing_dates is None:
      ticker_true_missing_dates = missing_dates.loc[time[0]:time[1]]
    else:
      ticker_true_missing_dates = pd.concat([ticker_true_missing_dates, missing_dates.loc[time[0]:time[1]]])
  return ticker_true_missing_dates

def _remove_tickers_with_no_missing_dates_while_in_sp500(true_missing_tickers_and_dates):
  true_missing_tickers_and_dates = {ticker: missing_dates  
                                    for ticker, missing_dates in true_missing_tickers_and_dates.items()
                                    if not missing_dates.empty}
  return true_missing_tickers_and_dates

def get_missing_occurances(true_missing_tickers_and_dates):
  all_dates = None
  for missing_dates in true_missing_tickers_and_dates.values():
    all_dates = pd.concat([all_dates, missing_dates])
  
  missing_occurances = pd.DataFrame(all_dates, columns=['Dates']).reset_index(drop=True)

  #Create a date range per year to bin
  start_date = dt.date(2007,1,1)
  end_date = dt.date.today() + relativedelta(years=1)
  date_range = pd.date_range(start_date, end_date, freq='YS') #YS or Y
  x_axis_labels = date_range[:-1].strftime('%Y')

  missing_occurances['Years'] = pd.cut(missing_occurances['Dates'],
                                      bins=date_range,
                                      labels=x_axis_labels)
  return missing_occurances, date_range

def format_tickers_and_missing_dates_for_json(full_missing_tickers_and_dates):
  formatted_full_missing_tickers_and_dates = dict()
  for ticker, missing_dates in full_missing_tickers_and_dates.items():
    #Need timestamps and lists to save file as jsons
    formatted_full_missing_tickers_and_dates[ticker] = missing_dates.apply(lambda x: x.timestamp()).values.tolist() 
  return  formatted_full_missing_tickers_and_dates