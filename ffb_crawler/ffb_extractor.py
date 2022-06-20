import logging
import csv
import requests
import pytz
from time import sleep
from locale import atof, setlocale, LC_NUMERIC
from datetime import datetime, date, timedelta, timezone

from build.gen.student.academic.v1.trade_pb2 import Trade
from ffb_producer import FfbProducer
from id_generator import company_id_generator, sha256

log = logging.getLogger(__name__)


def daterange(start_date: date, end_date: date):
    delta = timedelta(days=1)
    while start_date <= end_date:
        yield start_date
        start_date += delta


class FfbExtractor:
    def __init__(self, start_date: date, end_date: date):
        self.start_date = start_date
        self.end_date = end_date
        setlocale(LC_NUMERIC, "de_DE")
        self.producer = FfbProducer()

    def extract(self):
        log.info(f"running stock data extraction from FFB for dates {self.start_date} to {self.end_date}")
        # It is neccessary to skip non-weekdays, there is no error, but empty files downloaded
        for date in daterange(self.start_date, self.end_date):
            if self.is_weekday(date):
                try:
                    log.info(f"requesting csv for date {date}")
                    csv_data = self.send_request(date)
                    log.info(f"parsing csv for date {date}")
                    csv_reader = csv.DictReader(csv_data.splitlines(), delimiter=";")

                    i = 0
                    for trade in csv_reader:
                        proto_trade = self.parse_trade(trade)
                        self.producer.produce_to_topic(proto_trade)
                        i += 1
                    log.info(f"written {i} trade entries for date {date} to Kafka")
                except Exception as ex:
                    log.warn(f"extraction failed for date {date}", exc_info=True)
                    continue
            else:
                log.info(f"skipping date {date}, because it is a weekend day")

    def send_request(self, day):
        url = f"https://api.boerse-frankfurt.de/v1/data/derivatives_trade_history/day/csv?day={day}&language=de"
        # For graceful crawling! Remove this at your own risk!
        sleep(5)
        return requests.get(url=url).content.decode("utf-8-sig")

    def is_weekday(self, date: datetime.date) -> bool:
        if date.weekday() > 4:
            return False
        else:
            return True

    def parse_trade(self, trade) -> Trade:
        timezone = pytz.timezone("Europe/Berlin")
        time = datetime.strptime(trade["TIME"], "%d.%m.%Y %H:%M:%S")

        proto_trade = Trade()
        proto_trade.time = timezone.localize(time).isoformat()
        proto_trade.isin = trade["ISIN"]
        proto_trade.issuer = trade["ISSUER"]
        proto_trade.product_type = trade["PRODUCT TYPE"]
        proto_trade.underlying = trade["UNDERLYING"]
        proto_trade.price = atof(trade["PRICE"])
        proto_trade.volume = int(trade["VOLUME"])
        proto_trade.id = sha256(proto_trade.time + proto_trade.isin)
        return proto_trade
