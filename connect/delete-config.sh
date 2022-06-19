#!/bin/bash

KAFKA_CONNECT_ADDRESS=${1:-localhost}
KAFKA_CONNECT_PORT=${2:-8083}
KAFKA_CONNECT_API="$KAFKA_CONNECT_ADDRESS:$KAFKA_CONNECT_PORT/connectors"

# Remove RB corporate events connector
RB_ANNOUNCEMENTS_CONFIG=${3:-"$(dirname $0)/elastic-sink-rb_announcements.json"}
CONNECTOR_NAME=$(jq -r .name $RB_ANNOUNCEMENTS_CONFIG)
curl -Is -X DELETE $KAFKA_CONNECT_API/$CONNECTOR_NAME
RB_COMPANIES_CONFIG=${3:-"$(dirname $0)/elastic-sink-rb_companies.json"}
CONNECTOR_NAME=$(jq -r .name $RB_COMPANIES_CONFIG)
curl -Is -X DELETE $KAFKA_CONNECT_API/$CONNECTOR_NAME
RB_PERSONS_CONFIG=${3:-"$(dirname $0)/elastic-sink-rb_persons.json"}
CONNECTOR_NAME=$(jq -r .name $RB_PERSONS_CONFIG)
curl -Is -X DELETE $KAFKA_CONNECT_API/$CONNECTOR_NAME

# Remove FFB trade events connector
FFB_TRADE_CONFIG=${3:-"$(dirname $0)/elastic-sink-ffb_trade-events.json"}
CONNECTOR_NAME=$(jq -r .name $FFB_TRADE_CONFIG)
curl -Is -X DELETE $KAFKA_CONNECT_API/$CONNECTOR_NAME
