import logging
import os
from ffb_trade_processor.trade_processor import TradeProcessor

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"), format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)


def run():
    consumer = TradeProcessor()
    consumer.run()


if __name__ == "__main__":
    run()
