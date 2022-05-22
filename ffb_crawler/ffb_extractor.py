import logging
from time import sleep

import csv
import requests
from datetime import datetime

from build.gen.bakdata.stocks.stocks_pb2.py import Stocks
from ffb_producer import FfbProducer

class FfbExtractor:
    def __init__(self, start_date: str, end_date: str, day: str):		#Choose between time range or particular day
        self.start_date = self.str_to_date_object(start_date)
        self.end_date = self.str_to_date_object(end_date)
        self.one_day = self.str_to_date_object(day)
        #self.producer = FfbProducer()

    def extract(self):
        delta = datetime.timedelta(days=1)
        run_date = self.start_date
        while self.start_date <= self.end_date:       #It is neccessary to skip non-weekdays, there is no error, but empty files downloaded
            try:
                if (is_weekday(run_date)):
                    decoded_content = self.send_request(run_date)
                    cr = csv.reader(decoded_content.splitlines(), delimiter=';')
                    my_lists = list(cr)
                    
                    stocks = Stocks()

                    for list in my_lists:
                        print(list[0])
                        #stocks.time = list[0]
                        #stocks.isin = list[1]
                        #stocks.prodcut_type = list[2]
                        #stocks.issuer = list[3]
                        #stocks.underlying = list[4]
                        #stocks.price = list[5]
                        #stocks.volume = list[6]
                        print(list[6])
                        run_date += delta
                else:
                        run_date += delta
            except Exception as ex: 
                continue
        exit(0)

    def send_request(self, one_day):
        url = f"https://api.boerse-frankfurt.de/v1/data/derivatives_trade_history/day/csv?day={one_day}&language=de"
        # For graceful crawling! Remove this at your own risk!
        sleep(0.5)
        return requests.get(url=url).content.decode('utf-8')
        
    def is_weekday(self, date: datetime.date) -> boolean:
        if d.weekday() > 4:
	        return False
        else:
	        return True

    def str_to_date_object(self, date: str) -> datetime.date:
        d = datetime.strptime(date, '%Y-%m-%d').date()
        return d
