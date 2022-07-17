import logging
import sys

from confluent_kafka import DeserializingConsumer, SerializingProducer
from confluent_kafka.schema_registry.protobuf import ProtobufDeserializer, ProtobufSerializer
from confluent_kafka.serialization import StringDeserializer, StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient

from id_generator import company_id_generator, standardize_company_name
from build.gen.student.academic.v1.ffb_trade_pb2 import FFBTrade
from build.gen.student.academic.v1.company_pb2 import Company

from ffb_crawler.constant import BOOTSTRAP_SERVER, COMPANY_TOPIC, SCHEMA_REGISTRY_URL, TRADE_EVENT_TOPIC

FILTERED_TRADE_TOPIC = "ffb_filtered_trade-events"

log = logging.getLogger(__name__)


# consumer and producer
class TradeProcessor:

    def __init__(self):
        deserializer = ProtobufDeserializer(
            FFBTrade, {"use.deprecated.format": True}
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

        self.trade_producer = SerializingProducer({
            "bootstrap.servers": BOOTSTRAP_SERVER,
            "key.serializer": StringSerializer("utf_8"),
            "value.serializer":
                ProtobufSerializer(FFBTrade, schema_registry_client, {"use.deprecated.format": True}),
        })
        
        self.company_producer = SerializingProducer({
            "bootstrap.servers": BOOTSTRAP_SERVER,
            "key.serializer": StringSerializer("utf_8"),
            "value.serializer":
                ProtobufSerializer(Company, schema_registry_client, {"use.deprecated.format": True}),
        })

    def run(self):
        self.consume()

    def consume(self):
        log.info("Consuming FFBTrades")
        
        self.consumer.subscribe([TRADE_EVENT_TOPIC])
        try:
            while True:
                msg = self.consumer.poll(timeout=30.0)
                if msg is None:
                    log.info("waiting for next message")
                    continue
                if msg.error():
                    log.warn(msg.error())
                else:
                    self.processTrades(msg.value())
        except KeyboardInterrupt:
            sys.stderr.write('%% Aborted by user\n')
        finally:
            self.consumer.close()

    def processTrades(self, trade: FFBTrade):
        company = Company()
        company.name = trade.underlying.strip()
        company.std_name = standardize_company_name(company.name)
        company.id = company_id_generator(company.name)
        
        trade.company_id = company.id

        if company.name:
            self.produce(trade, company)

    def produce(self, 
        trade: FFBTrade, 
        company: Company
    ):
        # same class, but does not get accepted by serializer. why?
        whatEver = FFBTrade()
        whatEver.id = trade.id
        whatEver.time = trade.time
        whatEver.isin = trade.isin
        whatEver.issuer = trade.issuer
        whatEver.product_type = trade.product_type
        whatEver.underlying = trade.underlying
        whatEver.company_id = trade.company_id
        whatEver.price = trade.price
        whatEver.volume = trade.volume

        self.trade_producer.produce(
            topic=FILTERED_TRADE_TOPIC, partition=-1, key=str(whatEver.id), value=whatEver, on_delivery=self.delivery_report
        )
        self.trade_producer.poll()
        
        self.company_producer.produce(
            topic=COMPANY_TOPIC, partition=-1, key=str(company.id), value=company, on_delivery=self.delivery_report
        )
        self.company_producer.poll()
    

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
