#!/usr/bin/env sh

#HOST=localhost
HOST=192.168.0.26

## check if program mqttx is installed
if ! [ -x "$(command -v mqttx)" ]; then
  echo 'Error: mqttx is not installed. Please run "npm install mqttx-cli -g"' >&2
  exit 1
fi

## function to send an online message with a serialNumber parameter
send_online_state() {
  STATE_SERIAL_NUMBER=$1
  STATE_TOPIC="module/v1/ff/${STATE_SERIAL_NUMBER}/connection"
  echo "send online state for $1 to topic ${STATE_TOPIC}"
  STATE_MSG="{\"headerId\": 0,\"timestamp\": \"2023-03-24T13:58:37.781597Z\",\"version\": \"1.0.0\",\"manufacturer\": \"ff\",\"serialNumber\": \"${STATE_SERIAL_NUMBER}\",\"connectionState\": \"ONLINE\"}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${STATE_TOPIC}" -m "${STATE_MSG}"
}

## function to send an online message with a serialNumber parameter
send_online_state_fts() {
  STATE_SERIAL_NUMBER=$1
  STATE_TOPIC="fts/v1/ff/${STATE_SERIAL_NUMBER}/connection"
  echo "send online state for $1 to topic ${STATE_TOPIC}"
  STATE_MSG="{\"headerId\": 0,\"timestamp\": \"2023-03-24T13:58:37.781597Z\",\"version\": \"1.0.0\",\"manufacturer\": \"ff\",\"serialNumber\": \"${STATE_SERIAL_NUMBER}\",\"connectionState\": \"ONLINE\"}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${STATE_TOPIC}" -m "${STATE_MSG}"
}

send_state() {
  STATE_SERIAL_NUMBER=$1
  STATE_TOPIC="module/v1/ff/${STATE_SERIAL_NUMBER}/state"
  echo "send state for ${STATE_SERIAL_NUMBER} to topic ${STATE_TOPIC}"
  STATE_MSG="{\"timestamp\": \"2023-03-24T13:58:37.781597Z\",\"serialNumber\": \"${STATE_SERIAL_NUMBER}\",\"orderId\": \"\",\"orderUpdateId\": 0,\"paused\": false,\"errors\": []}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${STATE_TOPIC}" -m "${STATE_MSG}"
}

## send factsheet information for a serialNumber and a moduleType
send_factsheet_module() {
  FACT_SERIAL_NUMBER=$1
  FACT_MODULE_TYPE=$2
  FACT_TOPIC="module/v1/ff/${FACT_SERIAL_NUMBER}/factsheet"
  echo "send factsheet for ${FACT_SERIAL_NUMBER} to topic ${FACT_TOPIC}"
  FACT_MSG="{\"headerId\": 1,\"timestamp\": \"2023-03-24T13:58:37.781597Z\",\"version\": \"1.0.0\",\"manufacturer\": \"Fischertechnik\",\"serialNumber\": \"${FACT_SERIAL_NUMBER}\",\"typeSpecification\": {\"seriesName\": \"MOD-FF22+DRILL\",\"moduleClass\": \"${FACT_MODULE_TYPE}\"},\"physicalParameters\": {},\"protocolLimits\": {},\"protocolFeatures\": {\"moduleActions\": [{ \"actionType\": \"UNLOAD_WORKPIECE\" },{ \"actionType\": \"DRILL\", \"actionParameters\": [{ \"parameterName\": \"duration\", \"parameterType\": \"number\", \"parameterDescription\": \"Set the duration of the drilling operation\"}]}]},\"localizationParameters\": {},\"loadSpecification\": {\"loadSets\": [{\"setName\": \"WHITES\", \"loadType\": \"WHITE\"},{\"setName\": \"REDS\", \"loadType\": \"RED\"},{\"setName\": \"BLUES\", \"loadType\": \"BLUE\"}]}}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${FACT_TOPIC}" -m "${FACT_MSG}"
}

## sending factsheet for FTS for serialNumber
send_factsheet_fts() {
  FTS_SERIAL_NUMBER=$1
  FTS_TOPIC="fts/v1/ff/${FTS_SERIAL_NUMBER}/factsheet"
  echo "send factsheet for ${FTS_SERIAL_NUMBER} to topic ${FTS_TOPIC}"
  FTS_MSG="{\"headerId\": 1,\"timestamp\": \"2023-03-24T13:58:37.781597Z\",\"version\": \"1.0.0\",\"manufacturer\": \"Fischertechnik\",\"serialNumber\": \"${FTS_SERIAL_NUMBER}\",\"typeSpecification\": {\"seriesName\": \"FTS-FF22+\",\"agvClass\": \"CARRIER\",\"navigationTypes\": [\"PHYSICAL_LINE_GUIDED\"]},\"physicalParameters\": {},\"protocolLimits\": {},\"protocolFeatures\": {\"agvActions\": [{ \"actionType\": \"DOCK\", \"actionScopes\": \"NODE\" }]},\"agvGeometry\": {},\"localizationParameters\": {},\"loadSpecification\": {\"loadPositions\": [ \"LEFT\", \"MIDDLE\", \"RIGHT\" ],\"loadSets\": [{\"setName\": \"WHITES\", \"loadType\": \"WHITE\"},{\"setName\": \"REDS\", \"loadType\": \"RED\"},{\"setName\": \"BLUES\", \"loadType\": \"BLUE\"}]}}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${FTS_TOPIC}" -m "${FTS_MSG}"
}

send_state_fts() {
  FTS_SERIAL_NUMBER=$1
  FTS_TOPIC="fts/v1/ff/${FTS_SERIAL_NUMBER}/state"
  echo "send state for ${FTS_SERIAL_NUMBER} to topic ${FTS_TOPIC}"
  FTS_MSG="{\"timestamp\": \"2023-03-24T13:58:37.781597Z\",\"serialNumber\": \"${FTS_SERIAL_NUMBER}\",\"orderId\": \"\",\"orderUpdateId\": 0,\"paused\": false,\"errors\": [],\"lastNodeId\": \"2\",\"lastNodeSequenceId\": 0,\"nodeStates\": [],\"edgeStates\": [],\"driving\": false,\"batteryState\": {\"percentage\": 100},\"load\": []}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${FTS_TOPIC}" -m "${FTS_MSG}"
}

DPS_SERIAL_NUMBER="dpsSerial"
HBW_SERIAL_NUMBER="yBix"

#echo "Sending online states"
send_online_state ${DPS_SERIAL_NUMBER}
send_online_state ${HBW_SERIAL_NUMBER}
sleep 2

#echo "Sending factsheets"
send_factsheet_module ${DPS_SERIAL_NUMBER} "DPS"
send_factsheet_module ${HBW_SERIAL_NUMBER} "HBW"
sleep 2

#echo "Sendind current state information"
send_state ${DPS_SERIAL_NUMBER}
send_state ${HBW_SERIAL_NUMBER}
