import logging
from time import sleep

import requests
from id_generator import sha256
from parsel import Selector

from build.gen.student.academic.v1.rb_announcement_pb2 import RBAnnouncement, Status
from rb_crawler.rb_information_extractor import extract_related_data
from rb_producer import RbProducer

log = logging.getLogger(__name__)


class RbExtractor:
    def __init__(self, start_rb_id: int, state: str):
        self.rb_id = start_rb_id
        self.state = state
        self.producer = RbProducer()

    def extract(self):
        while True:
            try:
                log.info(f"Sending Request for: {self.rb_id} and state: {self.state}")
                text = self.send_request()
                if "Falsche Parameter" in text:
                    log.info("finished")
                    break
                selector = Selector(text=text)
                announcement = RBAnnouncement()
                announcement.rb_id = self.rb_id
                announcement.state = self.state
                identification = self.extract_identification(selector)
                announcement.court = identification["court"]
                announcement.reference_id = identification["entry_id"]
                event_type = selector.xpath("/html/body/font/table/tr[3]/td/text()").get()
                announcement.event_date = selector.xpath("/html/body/font/table/tr[4]/td/text()").get()
                announcement.id = sha256(self.state + str(self.rb_id))
                raw_text: str = selector.xpath("/html/body/font/table/tr[6]/td/text()").get()
                self.parse_event(announcement, event_type, raw_text)

                company = None
                persons = []
                if not announcement.event_type == "update" and announcement.information:
                    if announcement.reference_id.startswith("HRB"):
                        # HRB = capital venture
                        data = extract_related_data(raw_text)
                    
                        if data:
                            company = data["company"]
                            announcement.company_id = company.id
                            persons = data["persons"]
                        else:
                            log.warn(f"Could not parse company information from {self.rb_id} in state {self.state}")
                    else:
                        # HRA = individual merchant, ...
                        # ignore
                        pass
                
                self.producer.produce_to_topics(
                    announcement=announcement,
                    company=company,
                    persons=persons
                )
                self.rb_id = self.rb_id + 1
            except Exception as ex:
                raise ex
                log.error(f"Skipping {self.rb_id} in state {self.state}")
                log.error(f"Cause: {ex}")
                self.rb_id = self.rb_id + 1
                continue
        exit(0)

    def send_request(self) -> str:
        url = f"https://www.handelsregisterbekanntmachungen.de/skripte/hrb.php?rb_id={self.rb_id}&land_abk={self.state}"
        # For graceful crawling! Remove this at your own risk!
        sleep(0.5)
        return requests.get(url=url).text

    @staticmethod
    def extract_identification(selector: Selector) -> dict:
        title = selector.xpath("/html/body/font/table/tr[1]/td/nobr/u/text()").get()
        parts = title.split(": ")
        court = parts[0]
        return {
            "court": court[0:court.find("Aktenzeichen")].strip(),
            "entry_id": parts[1].strip()
        }

    def parse_event(self, announcement, event_type, raw_text):
        if event_type == "Neueintragungen":
            self.parse_new_entry_event(announcement, raw_text)
        elif event_type == "Veränderungen":
            self.parse_change_event(announcement, raw_text)
        elif event_type == "Löschungen":
            self.parse_delete_event(announcement)

    def parse_new_entry_event(self, announcement: RBAnnouncement, raw_text: str):
        log.debug(f"New company found: {announcement.id}")
        announcement.event_type = "create"
        announcement.information = raw_text
        announcement.status = Status.STATUS_ACTIVE

    def parse_change_event(self, announcement: RBAnnouncement, raw_text: str):
        log.debug(f"Changes are made to company: {announcement.id}")
        announcement.event_type = "update"
        announcement.status = Status.STATUS_ACTIVE
        announcement.information = raw_text

    def parse_delete_event(self, announcement: RBAnnouncement):
        log.debug(f"Company {announcement.id} is inactive")
        announcement.event_type = "delete"
        announcement.status = Status.STATUS_INACTIVE
