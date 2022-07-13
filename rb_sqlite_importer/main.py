import logging
from tkinter import E
import click
import os
import sqlite3
from id_generator import sha256

from build.gen.student.academic.v1.rb_announcement_pb2 import RBAnnouncement, Status
from rb_crawler.rb_producer import RbProducer

logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"), format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)
log = logging.getLogger(__name__)


@click.command()
@click.option("-i", "--input", "input_file", type=str)
def run(input_file: str):
    producer = RbProducer()
    conn = sqlite3.connect(input_file)

    cur = conn.cursor()
    cur.execute("SELECT * FROM \"corporate-events\"")

    for row in cur:
        announcement = RBAnnouncement()
        announcement.rb_id = row[1]
        announcement.state = row[2]
        announcement.court = row[3]
        announcement.reference_id = row[4]
        announcement.event_date = row[5]
        announcement.event_type = row[6]
        if row[7] == "STATUS_ACTIVE":
            announcement.status = Status.STATUS_ACTIVE
        elif row[7] == "STATUS_INACTIVE":
            announcement.status = Status.STATUS_INACTIVE
        else:
            announcement.status = Status.STATUS_UNSPECIFIED
        announcement.information = row[8]

        announcement.id = sha256(announcement.state + str(announcement.rb_id) + announcement.court)
        
        producer.produce_to_topics(announcement)


if __name__ == "__main__":
    run()
