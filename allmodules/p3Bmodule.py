def get_historical_batch_urls(tickers, date_length, IEX_TOKEN=IEX_TOKEN):
  '''Returns list of partitioned batch urls for api requests'''
  historical_batch_urls = []
  ticker_batches = [] #To have a recording of tickers in each batch

  for ticker_partition in _partition(tickers): #Partitioned for 50 tickers in each batch url 
    ticker_batches.append(ticker_partition)
    ticker_partition = ",".join(ticker_partition)
    #Batch Url should be changed to the respective sandbox mode url if you are testing if it works, you need to use a sandbox url
    batch_url = (f"https://cloud.iexapis.com/stable/stock/market/batch?symbols="
                + f"{ticker_partition}&types=chart&range={date_length}&token={IEX_TOKEN}")
    historical_batch_urls.append(batch_url)
  return historical_batch_urls, ticker_batches

def _partition(tickers, partition_size=50):
  partitioned_tickers = []
  for i in range(0, len(tickers), partition_size):
    partitioned_tickers.append(tickers[i:i+partition_size])
  return partitioned_tickers

def get_iex_historicals(hist_batch_urls):
  historicals = dict()
  key_error_log = []
  for hist_batch_url in hist_batch_urls:
    try:
      hist_response = requests.get(hist_batch_url)
      hist_response.raise_for_status()
      hist_response = hist_response.json()
    except requests.exceptions.RequestException as e:
      print('Stopped at batch url: {}'.format(hist_batch_url))
      print('Status Code: {}'.format(hist_response.status_code))
      raise SystemExit(e)
    for ticker in hist_response:
      ticker_hist = list()
      total_amount_of_days = len(hist_response[ticker]['chart'])
      for day in range(0, total_amount_of_days):
        current_date = hist_response[ticker]['chart'][day]['date']
        current_timestamp = dt.datetime.strptime(current_date,"%Y-%m-%d").timestamp() #Change to timestamp to save as hdf5
        try:
          ticker_hist.append([current_timestamp,
                            hist_response[ticker]['chart'][day]['fOpen'], #The 'f' in front of the OHLC names hash for the adjusted prices
                            hist_response[ticker]['chart'][day]['fHigh'], #fHigh is missing lol?
                            hist_response[ticker]['chart'][day]['fLow'],
                            hist_response[ticker]['chart'][day]['fClose'],
                            hist_response[ticker]['chart'][day]['fVolume']])
          historicals[ticker] = ticker_hist
        except KeyError as e:
          print("Key Error with {} at {} for {}".format(current_date, ticker, e))
          key_error_log.append([ticker, current_date, e])
      print('Finished downloading {}'.format(ticker))
  return historicals, key_error_log

def filter_out_historicals_missing_from_iex(historicals, sliced_ticker_batches):
  flat_ticker_batches = chain.from_iterable(sliced_ticker_batches) #Flatten it for a for loop
  
  missing_iex_tickers = [ticker 
                         for ticker in flat_ticker_batches
                         if ticker not in list(historicals.keys())] #Check for if tickers are missing
  
  empty_historical_tickers =  [ticker
                              for ticker, historicals in historicals.items()
                              if not historicals]
  return missing_iex_tickers, empty_historical_tickers

def add_missing_iex_tickers_to_historicals(historicals, missing_iex_tickers):
  for ticker in missing_iex_tickers:
    historicals[ticker] = []
  return historicals

def check_data_that_is_still_missing_from_batches(historicals, 
                                                  missing_iex_tickers,
                                                  full_missing_tickers_and_dates):
  data_still_missing = {ticker: np.setdiff1d(full_missing_tickers_and_dates[ticker], historicals[ticker])
                       for ticker in historicals}
  return data_still_missing

def convert_timestamps_to_datetimes(data_still_missing):
    data_still_missing = {ticker:
                                  [dt.date.fromtimestamp(missing_date)
                                  for missing_date in missing_dates]
                          for ticker, missing_dates in data_still_missing.items()}
    return data_still_missing
    
def calculate_data_reductions_from_iex(historicals,
                                      data_still_missing,
                                      full_missing_tickers_and_dates):

  amount_still_missing = {ticker: len(data_still_missing[ticker])
                          for ticker in historicals}
  total_still_missing = sum(amount_still_missing.values())

  amount_data_reductions = {ticker: len(full_missing_tickers_and_dates[ticker]) - len(data_still_missing[ticker])
                          for ticker in historicals}
  total_reductions = sum(amount_data_reductions.values())
  return (amount_still_missing, total_still_missing, amount_data_reductions, total_reductions)

def check_remaining_missing_tickers(data_still_missing):
  remaining_missing_tickers = []
  filled_tickers = []
  for ticker, dates in data_still_missing.items():
    if dates.size == 0:
      filled_tickers.append(ticker)
    else:
       remaining_missing_tickers.append(ticker)
  return remaining_missing_tickers, filled_tickers

def format_data_still_missing_for_json(data_still_missing):
  formatted_data_still_missing = dict()

  #Remove filled tickers as they are empty here (not missing anymore)
  for ticker in filled_tickers:
    data_still_missing.pop(ticker)

   #Need ndarray as list for json
  for ticker, missing_dates in data_still_missing.items():
    formatted_data_still_missing[ticker] = missing_dates.tolist()
  return  formatted_data_still_missing

def merge_historicals(yf_historicals, iex_historicals):
  historicals = dict()
  all_tickers = set(yf_historicals.keys()) + set(iex_historicals.keys())
  for ticker in all_tickers:
    historicals[ticker] = pd.concat([yf_historicals[ticker], iex_historicals[ticker]])
    historicals[ticker] = historicals[ticker].groupby(historicals[ticker].index).first().sort_index()
  return historicals

def test_for_ordinance(historicals):
  '''
  Description:
    Double check that the sort and merge worked

  Returns:
    - True if all the data is in chronological order
    - False if the data is not in chronological order
  '''
  ordinance = True
  for ticker in historicals:
    current_date = dt.date.min
    for date in historicals[ticker].index:
      if current_date > date or current_date == date:
        print('Error with ticker {} on {}'.format(ticker, date))
        ordinance = False
        return ordinance
      else:
        current_date = date
  return ordinance