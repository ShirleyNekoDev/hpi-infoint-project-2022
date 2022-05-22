import logging
import os

import click

from ffb_crawler.ffb_extractor import FfbExtractor

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"), format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)


@click.command()
@click.option("-s", "--start", "format is YYYY-MM-DD", type=str, help="The start date to initialize the crawl from")
@click.option("-e", "--end", "format is YYYY-MM-DD", type=str, help="The end date")
@click.option("-d", "--day", "format is YYYY-MM-DD", type=str, help="One particular day")
def run(start: str, end: str, day: str):
    FfbExtractor("2022-05-01", "2022-05.30").extract()


if __name__ == "__main__":
    run()
