import logging
import os

from rb_announcement_filter.announcement_filter import AnnouncementFilter

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"), format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)


def run():
    consumer = AnnouncementFilter()
    consumer.run()


if __name__ == "__main__":
    run()
