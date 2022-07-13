#!/bin/bash

KAFKA_CONNECT_ADDRESS=${1:-localhost}
KAFKA_CONNECT_PORT=${2:-8083}
KAFKA_CONNECT_API="$KAFKA_CONNECT_ADDRESS:$KAFKA_CONNECT_PORT/connectors"

CONNECTOR_CONFIG=${3:-"$(dirname $0)/elastic-sink.json"}
CONNECTOR_NAME=$(jq -r .name $RB_ANNOUNCEMENTS_CONFIG)
curl -Is -X DELETE $KAFKA_CONNECT_API/$CONNECTOR_NAME
