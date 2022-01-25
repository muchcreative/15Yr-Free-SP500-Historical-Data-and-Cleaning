## Part 1 - Collect Past SP500 Constituents

In order to get 15 Years of Historicals from the SP500 we first need to know which tickers we need to download historicals from. This means knowing the previous constituents that were in the SP500.

What is survivorship bias in stock trading? Pertaining to the SP500, as we backtest our data I will start backtesting around 2007. However, if you trade with the current SP500 tickers of 2022 and their daily prices in 2007 it would count as data leakage because your leaking the knowledge that the tickers of today did well enough from 2007 to 2022 to get into the SP500 at some point in time. However, this is not the case. In 2007 you did not know what tickers will do well, therefore it is up to us to account for these changes and trade the SP500 appropriately for the year you are backtesting in.

We need all the tickers that were ever in the SP500 and download all of their historicals for the past 15 years. We will then filter them and trade them at different points in time for our backtest. For now, let's focus on getting all the tickers that were ever in the SP500 and breakdown what's in the Part 1 folder.

The *"Part 1 Tutorial.ipynb"* is a python notebook written in Google Colab that will walk you through extracting an SP500 Changes CSV file to get all the tickers that were in the SP500 for a 15 year period and save it as a json file. We will also need to parse it and know what date tickers dropped and were added to the SP500 for backtesting later. This is all contained within Part 1 Tutorial Notebook. Additionally, the functions used in the notebook will be avaliable in the *"p1modules.py"* file and can be downloaded for easy use. The outputs of this tutorial, *"S&P500 Consitutents 20070101-20220116.json"* and *"S&P500 Changes 20070101-20220116.json"*, can be found in the *"p1outputs"* folder.

We will be using fja05680's *"S&P 500 Historical Components & Changes"* CSV file located [here](https://github.com/fja05680/sp500). Please download the latest csv version and ensure it has the dates you need in it, the one I downloaded is saved in the *"p1inputs"* folder but will not be updated, only used for reference.
