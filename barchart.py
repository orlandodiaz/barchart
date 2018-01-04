# Name: Barchart API
# Version: 1.0
# Description: Small wrapper around barchart's API

# Copyright 2018 Orlando Reategui

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging as log
import sys
from log import log
import urllib
import requests
import pandas as pd
import pytz
import requests.exceptions as ex
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from cred import token, backup_token


class Barchart(object):
    def __init__(self):
        self.token = token
        self.backup_token = backup_token

    def get_history(self, ticker, interval):
        """ description: Gets 5 min bar data  (as much as it can go)
            params: ticker, interval = daily, 5min
            output: will output json data
        """
        base_url = "https://marketdata.websol.barchart.com/getHistory.json?"

        # API settings
        options = {
            'apikey': self.token,
            'symbol': ticker,
            'maxRecords': "15000",
            'startDate' :  "20090203000000-06",
            'type': "minutes",
            'interval': "5",
            'order': "asc",
            'sessionFilter': "EFK",
            'dividends': "true",
            'splits': "true",
            'volume': "sum",
            'nearby': "1",
            'jerg' : "true",
        }

        if interval == "daily":
            options['type'] = 'daily'
            options['key'] = self.token # Your primary key
        elif interval == "5min":
            options['type'] = 'minutes'
            options['interval'] = "5"
            options['key'] = self.backup_token  # Another key to avoid going over the limit

        url = base_url + urllib.urlencode(options)

        try:
            log.info("%4s - Requesting %s data for ticker" % (ticker, interval))
            resp = requests.get(url)
            resp.raise_for_status()

        except ex.HTTPError:
            log.critical("%4s - HTTP Error encountered: %s" % (ticker, ex.HTTPError))

        except ex.Timeout:
            log.critical("%4s - Timeout ocurred " % ticker)

        except Exception as e:
            log.critical("%4s - Exception ocurred " % ticker)
            log.info(e)

        else:
            log.debug(resp.headers['Content-Type'])
            if 'json' not in resp.headers['Content-Type']:
                log.error("%4s - Server did not return a JSON response. More info on the debug section" % ticker)
                log.debug(resp.text)

                sys.exit()
                # raise ValueError("Server did not return a JSON response. Daily API limit most likely reached")
            else:
                data = resp.json()
                if data is None:
                    log.error("%4s - Data returned is NoneType" % ticker)

                elif not data:
                    log.error("%4s - Data returned is empty" % ticker)
                elif not data['results']:
                    log.error("%4s - No result field from json response. Most likely invalid ticker" % ticker)
                else:
                    log.info("%4s - SUCCESS" % ticker)
                    data = data['results']
                    return data

    def create_dataframe(self, data):
        """ description: Creates dataframe from data (barchart specifically)
            params: barchart RESP data
            output: stock dataframe
        """
        # Load data from dictionary received from requests
        df = pd.DataFrame.from_dict(data)

        # Only get the relevant columns in the correct order
        # bc_df = bc_df[['timestamp', 'open', 'high', 'low', 'close','volume']]
        df = df.reindex(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

        # Set the index to be the column timestamp
        df = df.set_index('timestamp')

        df.index = pd.to_datetime(df.index)

        # Convert to Eastern timezone
        eastern = pytz.timezone('US/Eastern')
        df.index = df.index.tz_localize(pytz.utc).tz_convert(eastern)

        return df


    def create_dictionary(self, tickers):
        """ description: synchronous way for making requests and building the dfs. Slow
            params: list of ticker strings
            output: dictionary of stock dataframes
        """
        stock_dict = {}
        for ticker in tickers:
            # Get the data
            data = self.get_history(ticker)
            # Build dataframe
            df = self.create_dataframe(data)
            # Store in dictionary
            stock_dict[ticker] = df
        return stock_dict


    def create_dict_async(self, data_dict):
        """ description: creates a dictionary dataframe of stocks from the data dictionary
            params: dictionary of stock data
            output: dataframe dictionary
        """

        dataframe_dict = {}
        log.debug("Building dataframe dictionary")
        for ticker in data_dict:
                data = data_dict[ticker].result()
                dataframe_dict[ticker] = self.create_dataframe(data)

        return dataframe_dict

    def create_data_dict_async(self, tickers, interval):
        """ description: asynchronous way to make multiple requests. 
            params: list of tickers
            output: data_dict, which is then passed create_dictionary_async
        """

        pool = ThreadPoolExecutor(3)
        intraday_dict = {}

        log.info('{0} stocks will be downloaded'.format(len(tickers)))
        for ticker in tickers:
            try:
                intraday_dict[ticker] = pool.submit(self.get_history, ticker, interval)
            except Exception as ex:
                log.debug(ex)

        return intraday_dict


if __name__ == '__main__':

    tickers = ["DCIX", "AAPL", "TWTR", "FB", "SNAP", "A"]

    barchart = Barchart()
    intraday_data = barchart.create_data_dict_async(tickers, "5min")
    intraday_dict = barchart.create_dict_async(intraday_data)

    # Intraday operations (synchronous)
    # intraday_data = create_data_async(tickers, "5min")
    # intraday_dict = create_dictionary_async(intraday_data)
    #
    # # Daily opertions (async)
    # daily_data = create_data_async(tickers, "daily")
    # daily_dict = create_dictionary_async(daily_data)

