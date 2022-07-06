import logging
import sys

from confluent_kafka import DeserializingConsumer, SerializingProducer
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer, ProtobufSerializer
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient

from build.gen.student.academic.v1.rb_announcement_pb2 import RBAnnouncement

from rb_crawler.constant import BOOTSTRAP_SERVER, ANNOUNCEMENT_TOPIC, SCHEMA_REGISTRY_URL

FILTERED_ANNOUNCEMENT_TOPIC = "rb_filtered_announcements"

log = logging.getLogger(__name__)

# consumer and producer
class AnnouncementFilter:

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
                    print(msg.error())
                else:
                    self.processAnnouncement(msg.value())
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.consumer.close()

    def processAnnouncement(self, announcement: RBAnnouncement):
        if announcement.information and announcement.company_id:
            print(f"Annoucement {announcement.rb_id}[{announcement.state}] has extracted company")
            self.produce(announcement)
        else:
            print(f"Annoucement {announcement.rb_id}[{announcement.state}] has no extracted company")

    def produce(self, announcement: RBAnnouncement):
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
        print(f"Annoucement {announcement.rb_id}[{announcement.state}] (re)pushed to Kafka")

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
