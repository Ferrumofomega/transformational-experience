# Flask on Heroku 
This repository contains a simple Flask app that runs on Heroku and plots graphs using Bokeh.
The app takes as input a stock ticker code (and optional start year) and displays a Bokeh plot of the stock time series. 
Stock price data comes from the [WIKI database](https://www.quandl.com/data/WIKI), queried via the requests module.
