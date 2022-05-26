from datetime import datetime, date
import logging
import os

import click

from ffb_crawler.ffb_extractor import FfbExtractor

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"), format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)


class Date(click.ParamType):
    name = "date"

    def __init__(self):
        self.formats = ["%Y-%m-%d", "%d.%m.%Y"]

    def get_metavar(self, param):
        return "[{}]".format("|".join(self.formats))

    def _try_to_convert_date(self, value, format):
        try:
            return datetime.strptime(value, format).date()
        except ValueError:
            return None

    def convert(self, value, param, ctx):
        for format in self.formats:
            date = self._try_to_convert_date(value, format)
            if date:
                return date

        self.fail("invalid date format: {}. (choose from {})".format(value, ", ".join(self.formats)))

    def __repr__(self):
        return "Date"


# "format is YYYY-MM-DD",
@click.command()
@click.option(
    "-s",
    "--start-date",
    type=Date(),
    help="Start date to initialize the crawl from, defaults to today",
    default=str(date.today()),
)
@click.option("-e", "--end-date", type=Date(), help="End date", default=str(date.today()))
def run(start_date: Date, end_date: Date):
    FfbExtractor(start_date, end_date).extract()


if __name__ == "__main__":
    run()
