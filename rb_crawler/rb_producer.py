import logging

from confluent_kafka import SerializingProducer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.protobuf import ProtobufSerializer
from confluent_kafka.serialization import StringSerializer

from build.gen.student.academic.v1.rb_announcement_pb2 import RBAnnouncement
from build.gen.student.academic.v1.rb_company_pb2 import RBCompany
from build.gen.student.academic.v1.rb_person_pb2 import RBPerson
from rb_crawler.constant import SCHEMA_REGISTRY_URL, BOOTSTRAP_SERVER, ANNOUNCEMENT_TOPIC, COMPANY_TOPIC, PERSON_TOPIC

log = logging.getLogger(__name__)


class RbProducer:
    def __init__(self):
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
                ProtobufSerializer(RBCompany, schema_registry_client, {"use.deprecated.format": True}),
        })
        self.person_producer = SerializingProducer({
            "bootstrap.servers": BOOTSTRAP_SERVER,
            "key.serializer": StringSerializer("utf_8"),
            "value.serializer":
                ProtobufSerializer(RBPerson, schema_registry_client, {"use.deprecated.format": True}),
        })

    def produce_to_topics(self, 
        announcement: RBAnnouncement,
        company: RBCompany,
        persons: "list[RBPerson]"
    ):
        self.announcement_producer.produce(
            topic=ANNOUNCEMENT_TOPIC, partition=-1, key=str(announcement.id), value=announcement, on_delivery=self.delivery_report
        )
        if company:
            self.company_producer.produce(
                topic=COMPANY_TOPIC, partition=-1, key=str(company.id), value=company, on_delivery=self.delivery_report
            )
            self.company_producer.poll()

            for person in persons:
                self.person_producer.produce(
                    topic=PERSON_TOPIC, partition=-1, key=str(person.id), value=person, on_delivery=self.delivery_report
                )
            if persons:
                self.person_producer.poll()

        # It is a naive approach to flush after each produce this can be optimised
        self.announcement_producer.poll()

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
