#!/bin/bash

KAFKA_CONNECT_ADDRESS=${1:-localhost}
KAFKA_CONNECT_PORT=${2:-8083}
CORPORATE_CONFIG=${3:-"$(dirname $0)/elastic-sink-corporate.json"}
TRADE_CONFIG=${3:-"$(dirname $0)/elastic-sink-trade.json"}
KAFKA_CONNECT_API="$KAFKA_CONNECT_ADDRESS:$KAFKA_CONNECT_PORT/connectors"

# Create corporate events connector
data=$(cat $CORPORATE_CONFIG | jq -s '.[0]')
curl -X POST $KAFKA_CONNECT_API --data "$data" -H "content-type:application/json"

# Create trade events connector
data=$(cat $TRADE_CONFIG | jq -s '.[0]')
curl -X POST $KAFKA_CONNECT_API --data "$data" -H "content-type:application/json"
