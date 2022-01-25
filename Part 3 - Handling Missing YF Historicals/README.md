## Part 3 - Handling Missing YF Historicals

As per Part 2, in this section we will go over what to do with our missing tickers that were not avaliable off of Yahoo Finance. Additionally, we must inspect the data we did download and check that all the data is there for the time that the tickers are in the SP500. Once inspected we will go over ways to handle missing data and if possible, find ways to procure the missing information.

Tutorial 3A will be about the missing EDA. We will inspect common problems with the missing data and the inevitable problems with YF and free data. It will also provide you with some options on how to deal with the missing data

Tutorial 3B will be a sample excerpt on how to download historicals from a REST API. The API used will be IEX Cloud. However, you will see that only 10-15% of the missing data can be filled from a database with most likely decreasing returns if you keep downloading from different database. I suggest using manual research for the last remaining tickers to check for updated ticker names or lost historical data. Additionally, an extra database can be used to cross reference and check your data against Yahoo Finance and may be useful for a data pipeline to check the quality of your data.

This is the last part of the tutorial and after this you should have a good start to your SP500 data and ideas on the characteristics of your missing data. You will also understand that trading stocks especially using this strategy for backtesting will require work, but you may be able to come up with a strategy that works or can adapt to the changing times of the stock market. Best of luck.
