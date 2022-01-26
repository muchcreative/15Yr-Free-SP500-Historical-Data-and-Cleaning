## Introduction

The intended purpose of this dataset to trade and select stocks on the SP500 as it changes through the years and create a strategy that can select good stocks to buy on the SP500 at any point in history. This key issue here is that the SP500 changes through the years and this must be accounted for to prevent Survivorship Bias. Using the current SP500 stocks to start trading 15 years ago is cheating as you will have data leakage knowing the SP500 stocks of today. These tutorials will help give you a good place to start a rotating SP500 dataset for your backtesting or machine learning networks.

The dataset can be used with a backtester to test out a strategy or used to train a machine learning program. Its main focus will be trading the SP500. If you later plan on using a paid for service that utlizes a REST API, I have uploaded IEX Cloud API request functions in the Part 3B Tutorial for reference.

You will need to incorporate your own data pipeline to check the quality of the historicals once you downloaded them yourself. Additionally, the majority of tickers can be download off of YF and even a paid service. However, for tickers dating back to 2007-2010, you will need to manually research changes in ticker names as they can often be considerd invalid when you request for them. For example, m&a or bankrupticies of a company tend to get deleted or renamed on an online database. You will see this in Part 3 of the tutorial.

Thanks to fja05680 for the SP500 constituents changes list located here https://github.com/fja05680/sp500 and the free yf-finance module released here https://github.com/ranaroussi/yfinance by Ran Aroussi.

Disclaimer: Personally I do not use Yahoo Finance Data for a multitude of reasons. First the OHLC (Open, High, Low, Close Prices, Volume) are not fully adjusted. Although setting "auto_adjust=True" in the yf-module solves this, I am still unsure about the quality of the YF data and the fact that the YF API owned by Yahoo is discontinued. Additionally, some data points and tickers are missing as you will find out when we start cleaning the data. This is especially true as Yahoo tends to delete ticker historicals that were involved in bankruptcies, mergers, buyouts, or name changes not accounted for in fja05680s' list. But if you are starting out, YF is fine for your initial start. I prefer a REST API such as IEX, Polygon, or Alpaca over Yahoo Finance but even they have missing data. However, they are very affordable, offer more than just historicals, have fast download speed, and provide customer support. Alternatively, if you are in a university you may be able to access a Bloomberg Portal or Capital IQ for free if your university offers it.

## Breakdown

The "*allmodules"* folder has all functions that we will use in the tutorials. Still, the tutorials have their own module folders to store all the functions that they use.

**Part 1: Collect Past SP500 Constituents**

Determines which stocks we will need to download and tells us which tickers will rotate in and out of the SP500 as you backtest.

**Part 2: Download YF Historicals**

Downloads YF historicals in a safe manner that records which tickers that are missing from the Yahoo Finance and which ones we have.

**Part 3: Handling Missing YF Historicals**

EDA on the missing data and tips on how you can handle your missing data. Additionally, it goes over how to download historicals from a REST API, specifically IEX Cloud.
