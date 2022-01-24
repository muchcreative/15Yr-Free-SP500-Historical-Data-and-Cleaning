## Introduction

The intended purpose of this dataset is to use this to trade and select stocks on the SP500 as it changes through the years and create a strategy that can select good stocks to buy on the SP500 at any point in history. The dataset can be used with a backtester to test out a strategy or used to train a machine learning program. Its main focus will be trading the SP500. If you plan on using a paid for service that utlizes a REST API, I have my IEX Cloud API requested in Part 3B Tutorial for reference.

Let me know if you have any questions

Thanks to fja05680 for the SP500 constituents changes list located here https://github.com/fja05680/sp500 and the free yf-finance module released here https://github.com/ranaroussi/yfinance by Ran Aroussi.

Disclaimer: I personally do not use Yahoo Finance Data for a multitude of reasons. First the OHLC (Open, High, Low, Close Prices) are not fully adjusted. Although setting "auto_adjust=True" in the yf-module solves this, I am still unsure about the quality of the YF data and the fact that the YF API owned by Yahoo is discontinued. Additionally, some data points and tickers are missing as you will find out when we start cleaning the data. This is especially true as Yahoo tends to delete ticker historicals that were involved in bankruptcies, mergers, buyouts, or name changes. But if you are starting out, YF is fine for your initial start as you will soon find even paid services tend to lack some data points.

I prefer a REST API such as IEX, Polygon, or Alpaca over Yahoo Finance. They are very affordable, offer more than just historicals, faster download speed, and provide customer support. Alternatively, if you are in a university you may be able to access a Bloomberg Portal or Capital IQ for free if your university offers it.

## Breakdown

The "*allmodules"* folder has all functions that we will use in the tutorials for easier digestion and integration for your programs. Still, the tutorials have their own module folders to store all the functions that they use. This is to avoid back-tracing to this folder.

**Part 1: Collect Past SP500 Constituents**

Determines which stocks we will download and tells us which tickers will drop in and out of the sp500 as you backtest your strategy through the years.

**Part 2: Download YF Historicals**

Downloads YF historicals in a safe manner that records which tickers that are missing from the SP500 and which ones we have.

**Part 3: Handling Missing YF Historicals**

EDA on the missing data and tips on how you could handle your missing data.
