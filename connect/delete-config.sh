#!/bin/bash

KAFKA_CONNECT_ADDRESS=${1:-localhost}
KAFKA_CONNECT_PORT=${2:-8083}
CORPORATE_CONFIG=${3:-"$(dirname $0)/elastic-sink-corporate.json"}
TRADE_CONFIG=${3:-"$(dirname $0)/elastic-sink-trade.json"}
KAFKA_CONNECT_API="$KAFKA_CONNECT_ADDRESS:$KAFKA_CONNECT_PORT/connectors"

# Remove corporate events connector
CONNECTOR_NAME=$(jq -r .name $CORPORATE_CONFIG)
curl -Is -X DELETE $KAFKA_CONNECT_API/$CONNECTOR_NAME

# Remove trade events connector
CONNECTOR_NAME=$(jq -r .name $TRADE_CONFIG)
curl -Is -X DELETE $KAFKA_CONNECT_API/$CONNECTOR_NAME
