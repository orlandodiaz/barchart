
###  Description
Pull 5-min or daily historical data from barchart historical API

###  Usage
You will first need a token, which you must request from the barchart website. Resulting output is a dictionary of stocks
with their correct corresponding pandas dataframe. 


### Examples

    barchart = Barchart()

    tickers = ["DCIX", "AAPL", "TWTR", "FB", "SNAP", "A"]
     
    # 5-min data
    intraday_data = barchart.create_data_dict_async(tickers, "5min")
    intraday_dict = barchart.create_dict_async(intraday_data)
    
     
    intraday_dict['TWTR'].tail(5)
    Out[9]: 
                                  open    high     low    close  volume
    timestamp                                                          
    2018-01-03 11:35:00-05:00  24.2200  24.265  24.220  24.2401  126815
    2018-01-03 11:40:00-05:00  24.2450  24.280  24.240  24.2790   75429
    2018-01-03 11:45:00-05:00  24.2800  24.280  24.250  24.2600   88249
    2018-01-03 11:50:00-05:00  24.2599  24.325  24.255  24.2850  115589
    2018-01-03 11:55:00-05:00  24.2900  24.380  24.270  24.3800  197003
     
    # Correct datatypes and index 
    intraday_dict['TWTR'].dtypes
    Out[10]: 
    open      float64
    high      float64
    low       float64
    close     float64
    volume      int64
    dtype: object
     
    Out[13]: 
    DatetimeIndex(['2017-10-04 09:30:00-04:00',
    '2018-01-03 11:50:00-05:00', '2018-01-03 11:55:00-05:00'],
    dtype='datetime64[ns, US/Eastern]', name=u'timestamp', length=4858, freq=None)

    
    


    
