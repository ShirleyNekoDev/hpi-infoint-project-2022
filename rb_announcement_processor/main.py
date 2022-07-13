import logging
import os

from rb_announcement_processor.announcement_processor import AnnouncementProcessor

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"), format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)


def run():
    consumer = AnnouncementProcessor()
    consumer.run()


if __name__ == "__main__":
    run()
