import logging
import sys

from confluent_kafka import DeserializingConsumer, SerializingProducer
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer, ProtobufSerializer
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient

from build.gen.student.academic.v1.rb_announcement_pb2 import RBAnnouncement
from build.gen.student.academic.v1.company_pb2 import Company
from build.gen.student.academic.v1.rb_person_pb2 import RBPerson
from rb_announcement_processor.rb_information_extractor import extract_company, extract_personnel

from rb_crawler.constant import BOOTSTRAP_SERVER, ANNOUNCEMENT_TOPIC, COMPANY_TOPIC, PERSON_TOPIC, SCHEMA_REGISTRY_URL

FILTERED_ANNOUNCEMENT_TOPIC = "rb_filtered_announcements"

log = logging.getLogger(__name__)


# consumer and producer
class AnnouncementProcessor:

    def __init__(self):
        deserializer = ProtobufDeserializer(
            RBAnnouncement, {"use.deprecated.format": True}
        )

        string_deserializer = StringDeserializer("utf_8")
        config = {
            'bootstrap.servers': BOOTSTRAP_SERVER,
            'key.deserializer': string_deserializer,
            'value.deserializer': deserializer,
            'group.id': "rb_announcement-filter-group",
            'session.timeout.ms': 6000,
            'auto.offset.reset': 'earliest'
        }

        self.consumer = DeserializingConsumer(conf=config)
        
        schema_registry_conf = {"url": SCHEMA_REGISTRY_URL}
        schema_registry_client = SchemaRegistryClient(schema_registry_conf)

        self.announcement_producer = SerializingProducer({
            "bootstrap.servers": BOOTSTRAP_SERVER,
            "key.serializer": StringSerializer("utf_8"),
            "value.serializer":
                ProtobufSerializer(RBAnnouncement, schema_registry_client, {"use.deprecated.format": True}),
        })
        
        self.company_producer = SerializingProducer({
            "bootstrap.servers": BOOTSTRAP_SERVER,
            "key.serializer": StringSerializer("utf_8"),
            "value.serializer":
                ProtobufSerializer(Company, schema_registry_client, {"use.deprecated.format": True}),
        })

        self.person_producer = SerializingProducer({
            "bootstrap.servers": BOOTSTRAP_SERVER,
            "key.serializer": StringSerializer("utf_8"),
            "value.serializer":
                ProtobufSerializer(RBPerson, schema_registry_client, {"use.deprecated.format": True}),
        })

    def run(self):
        self.consume()

    def consume(self):
        log.info("Consuming RBAnnouncement")
        
        self.consumer.subscribe([ANNOUNCEMENT_TOPIC])
        try:
            while True:
                msg = self.consumer.poll(timeout=10.0)
                if msg is None:
                    continue
                if msg.error():
                    log.warn(msg.error())
                else:
                    self.processAnnouncement(msg.value())
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.consumer.close()

    def processAnnouncement(self, announcement: RBAnnouncement):
        if announcement.information:
            if announcement.reference_id.startswith("HRB"):
                # HRB = capital venture
                company = None
                company_data = extract_company(announcement.information)
                end_of_match = 0
                if company_data:
                    company = company_data["company"]
                    end_of_match = company_data["end_of_match"]
                    announcement.company_id = company.id

                persons_and_positions_data = extract_personnel(announcement.information[end_of_match:])
                if company:
                    company.position.extend(persons_and_positions_data["positions"])
                persons = persons_and_positions_data["persons"]
            
                log.info(f"Parsed {announcement.rb_id} / {announcement.state}")
                self.produce(announcement, company, persons)
            else:
                # HRA = individual merchant, ...
                log.info(f"Skipped {announcement.rb_id} / {announcement.state} - not HRB")
        else:
            log.info(f"Skipped {announcement.rb_id} / {announcement.state} - empty information field")

    def produce(self, 
        announcement: RBAnnouncement, 
        company: Company, 
        persons
    ):
        # same class, but does not get accepted by serializer. why?
        whatEver = RBAnnouncement()
        whatEver.id = announcement.id
        whatEver.rb_id = announcement.rb_id
        whatEver.state = announcement.state
        whatEver.court = announcement.court
        whatEver.reference_id = announcement.reference_id
        whatEver.event_date = announcement.event_date
        whatEver.event_type = announcement.event_type
        whatEver.status = announcement.status
        whatEver.information = announcement.information
        whatEver.company_id = announcement.company_id

        self.announcement_producer.produce(
            topic=FILTERED_ANNOUNCEMENT_TOPIC, partition=-1, key=str(whatEver.id), value=whatEver, on_delivery=self.delivery_report
        )
        self.announcement_producer.poll()
        # log.info(f"Annoucement {announcement.rb_id} / {announcement.state} (re)pushed to Kafka")
        
        if company:
            self.company_producer.produce(
                topic=COMPANY_TOPIC, partition=-1, key=str(company.id), value=company, on_delivery=self.delivery_report
            )
            self.company_producer.poll()
            # log.info(f"Company {company.id} \"{company.name}\" pushed to Kafka")
        
        for person in persons:
            self.person_producer.produce(
                topic=PERSON_TOPIC, partition=-1, key=str(person.id), value=person, on_delivery=self.delivery_report
            )
            # log.info(f"Person {person.id} pushed to Kafka")
        if persons:
            self.person_producer.poll()

    @staticmethod
    def delivery_report(err, msg):
        """
        Reports the failure or success of a message delivery.
        Args:
            err (KafkaError): The error that occurred on None on success.
            msg (Message): The message that was produced or failed.
        Note:
            In the delivery report callback the Message.key() and Message.value()
            will be the binary format as encoded by any configured Serializers and
            not the same object that was passed to produce().
            If you wish to pass the original object(s) for key and value to delivery
            report callback we recommend a bound callback or lambda where you pass
            the objects along.
        """
        if err is not None:
            log.error("Delivery failed for User record {}: {}".format(msg.key(), err))
            return
        log.info(
            "User record {} successfully produced to {} [{}] at offset {}".format(
                msg.key(), msg.topic(), msg.partition(), msg.offset()
            )
        )
