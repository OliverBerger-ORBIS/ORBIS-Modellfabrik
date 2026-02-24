#!/usr/bin/env sh

HOST=localhost
#HOST=192.168.0.26

## check if program mqttx is installed
if ! [ -x "$(command -v mqttx)" ]; then
  echo 'Error: mqttx is not installed. Please run "npm install mqttx-cli -g"' >&2
  exit 1
fi

## function to send an online message with a serialNumber parameter
send_online_state() {
  STATE_SERIAL_NUMBER=$1
  STATE_TOPIC="module/v1/ff/${STATE_SERIAL_NUMBER}/connection"
  RAND=$(od -An -N1 -i /dev/random | tr -d '[:space:]')
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "send online state for $1 to topic ${STATE_TOPIC}"
  STATE_MSG="{\"headerId\": 0,\"timestamp\": \"${TIMESTAMP}\",\"version\": \"1.0.0\",\"ip\":\"192.168.0.${RAND}\",\"manufacturer\": \"ff\",\"serialNumber\": \"${STATE_SERIAL_NUMBER}\",\"connectionState\": \"ONLINE\"}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${STATE_TOPIC}" -m "${STATE_MSG}"
}

## function to send an online message with a serialNumber parameter
send_online_state_no_ip_and_version() {
  STATE_SERIAL_NUMBER=$1
  STATE_TOPIC="module/v1/ff/${STATE_SERIAL_NUMBER}/connection"
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "send online state for $1 to topic ${STATE_TOPIC}"
  STATE_MSG="{\"headerId\": 0,\"timestamp\": \"${TIMESTAMP}\",\"manufacturer\": \"ff\",\"serialNumber\": \"${STATE_SERIAL_NUMBER}\",\"connectionState\": \"ONLINE\"}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${STATE_TOPIC}" -m "${STATE_MSG}"
}

## function to send an online message with a serialNumber parameter
send_online_state_fts() {
  STATE_SERIAL_NUMBER=$1
  STATE_TOPIC="fts/v1/ff/${STATE_SERIAL_NUMBER}/connection"
  RAND=$(od -An -N1 -i /dev/random | tr -d '[:space:]')
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "send online state for $1 to topic ${STATE_TOPIC}"
  STATE_MSG="{\"headerId\": 0,\"timestamp\": \"${TIMESTAMP}\",\"version\": \"1.0.0\",\"ip\":\"192.168.0.${RAND}\",\"manufacturer\": \"ff\",\"serialNumber\": \"${STATE_SERIAL_NUMBER}\",\"connectionState\": \"ONLINE\"}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${STATE_TOPIC}" -m "${STATE_MSG}"
}

send_state() {
  STATE_SERIAL_NUMBER=$1
  STATE_TOPIC="module/v1/ff/${STATE_SERIAL_NUMBER}/state"
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "send state for ${STATE_SERIAL_NUMBER} to topic ${STATE_TOPIC}"
  STATE_MSG="{\"timestamp\": \"${TIMESTAMP}\",\"serialNumber\": \"${STATE_SERIAL_NUMBER}\",\"orderId\": \"\",\"orderUpdateId\": 0,\"paused\": false,\"errors\": []}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${STATE_TOPIC}" -m "${STATE_MSG}"
}

send_error_state() {
  STATE_SERIAL_NUMBER=$1
  ERROR_ACTION=$2
  STATE_TOPIC="module/v1/ff/${STATE_SERIAL_NUMBER}/state"
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "send error state for ${STATE_SERIAL_NUMBER} to topic ${STATE_TOPIC}"
  STATE_MSG="{\"timestamp\": \"${TIMESTAMP}\",\"serialNumber\": \"${STATE_SERIAL_NUMBER}\",\"orderId\": \"\",\"orderUpdateId\": 0,\"paused\": false,\"errors\": [{\"errorType\": \"${ERROR_ACTION}_error\", \"timestamp\": \"${TIMESTAMP}\", \"errorLevel\": \"FATAL\", \"errorReferences\": [] }]}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${STATE_TOPIC}" -m "${STATE_MSG}"
}


send_calibration_state() {
  STATE_SERIAL_NUMBER=$1
  STATE_TOPIC="module/v1/ff/${STATE_SERIAL_NUMBER}/state"
  echo "send state for ${STATE_SERIAL_NUMBER} to topic ${STATE_TOPIC}"
  STATE_MSG="{\"timestamp\": \"2023-03-24T13:58:37.781597Z\",\"serialNumber\": \"${STATE_SERIAL_NUMBER}\",\"orderId\": \"\",\"orderUpdateId\": 0,\"paused\": true,\"errors\": [],\"information\": [{\"infoType\": \"calibration_data\", \"infoLevel\": \"DEBUG\", \"infoReferences\": [{\"referenceKey\":\"TEST\", \"referenceValue\": 123}] }, {\"infoType\": \"calibration_status\", \"infoLevel\": \"DEBUG\", \"infoReferences\": [{\"referenceKey\":\"POSITIONS.AVAILABLE\", \"referenceValue\": \"A,B\"}] }]}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${STATE_TOPIC}" -m "${STATE_MSG}"
}


## send factsheet information for a serialNumber and a moduleType
send_factsheet_module() {
  FACT_SERIAL_NUMBER=$1
  FACT_MODULE_TYPE=$2
  FACT_CLEAR_MODULE_PICK=$3
  if [ "$4" = "calibrate" ] ; then
    FACT_MODULE_CALIBRATION="{ \"actionType\": \"startCalibration\" },"
  else
    FACT_MODULE_CALIBRATION=""
  fi
  FACT_TOPIC="module/v1/ff/${FACT_SERIAL_NUMBER}/factsheet"
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "send factsheet for ${FACT_SERIAL_NUMBER} to topic ${FACT_TOPIC}"
  FACT_MSG="{\"headerId\": 1,\"timestamp\": \"${TIMESTAMP}\",\"version\": \"1.0.0\",\"manufacturer\": \"Fischertechnik\",\"serialNumber\": \"${FACT_SERIAL_NUMBER}\",\"typeSpecification\": {\"seriesName\": \"MOD-FF22+${FACT_MODULE_TYPE}\",\"moduleClass\": \"${FACT_MODULE_TYPE}\"},\"physicalParameters\": {},\"protocolLimits\": {},\"protocolFeatures\": {\"moduleParameters\": {\"clearModuleOnPick\": ${FACT_CLEAR_MODULE_PICK}, \"moduleActions\": [{ \"actionType\": \"UNLOAD_WORKPIECE\" },{ \"actionType\": \"DRILL\", \"actionParameters\": [{ \"parameterName\": \"duration\", \"parameterType\": \"number\", \"parameterDescription\": \"Set the duration of the drilling operation\"}]}]}},\"localizationParameters\": {},\"loadSpecification\": {\"loadSets\": [{\"setName\": \"WHITES\", \"loadType\": \"WHITE\"},{\"setName\": \"REDS\", \"loadType\": \"RED\"},{\"setName\": \"BLUES\", \"loadType\": \"BLUE\"}]}}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${FACT_TOPIC}" -m "${FACT_MSG}"
}

## sending factsheet for FTS for serialNumber
send_factsheet_fts() {
  FTS_SERIAL_NUMBER=$1
  FTS_TOPIC="fts/v1/ff/${FTS_SERIAL_NUMBER}/factsheet"
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "send factsheet for ${FTS_SERIAL_NUMBER} to topic ${FTS_TOPIC}"
  FTS_MSG="{\"headerId\": 1,\"timestamp\": \"${TIMESTAMP}\",\"version\": \"1.0.0\",\"manufacturer\": \"Fischertechnik\",\"serialNumber\": \"${FTS_SERIAL_NUMBER}\",\"typeSpecification\": {\"seriesName\": \"FTS-FF22+\",\"agvClass\": \"CARRIER\",\"navigationTypes\": [\"PHYSICAL_LINE_GUIDED\"]},\"physicalParameters\": {},\"protocolLimits\": {},\"protocolFeatures\": {\"agvActions\": [{ \"actionType\": \"DOCK\", \"actionScopes\": \"NODE\" }]},\"agvGeometry\": {},\"localizationParameters\": {},\"loadSpecification\": {\"loadPositions\": [ \"LEFT\", \"MIDDLE\", \"RIGHT\" ],\"loadSets\": [{\"setName\": \"WHITES\", \"loadType\": \"WHITE\"},{\"setName\": \"REDS\", \"loadType\": \"RED\"},{\"setName\": \"BLUES\", \"loadType\": \"BLUE\"}]}}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${FTS_TOPIC}" -m "${FTS_MSG}"
}

send_state_fts() {
  FTS_SERIAL_NUMBER=$1
  FTS_DOCKED_SERIAL=$2
  if [ -z "$2" ]; then
    FTS_DOCKED_SERIAL="UNKNOWN"
  fi
  FTS_TOPIC="fts/v1/ff/${FTS_SERIAL_NUMBER}/state"
  TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "send state for ${FTS_SERIAL_NUMBER} to topic ${FTS_TOPIC}"
  FTS_MSG="{\"timestamp\": \"${TIMESTAMP}\",\"serialNumber\": \"${FTS_SERIAL_NUMBER}\",\"orderId\": \"\",\"orderUpdateId\": 0,\"paused\": false,\"errors\": [],\"lastNodeId\": \"${FTS_DOCKED_SERIAL}\",\"lastNodeSequenceId\": 0,\"nodeStates\": [],\"edgeStates\": [],\"driving\": false,\"batteryState\": {\"percentage\": 100},\"load\": []}"
  mqttx pub -h $HOST -p 1883 -u default -P default -t "${FTS_TOPIC}" -m "${FTS_MSG}"
}

FTS_SERIAL_NUMBER="eBix"
DRILL_SERIAL_NUMBER="xULx"
MILL_SERIAL_NUMBER="4qjs"
HBW_SERIAL_NUMBER="yBix"
AIQS_SERIAL_NUMBER="4Cjx"
DPS_SERIAL_NUMBER="eQw0"
OVEN_SERIAL_NUMBER="iKw0"

#echo "Sending online states"
send_online_state_fts ${FTS_SERIAL_NUMBER}
# send_online_state ${DRILL_SERIAL_NUMBER}
send_online_state_no_ip_and_version ${DRILL_SERIAL_NUMBER}
send_online_state ${MILL_SERIAL_NUMBER}
# send_online_state ${HBW_SERIAL_NUMBER}
send_online_state_no_ip_and_version ${HBW_SERIAL_NUMBER}
send_online_state ${AIQS_SERIAL_NUMBER}
# send_online_state ${DPS_SERIAL_NUMBER}
send_online_state_no_ip_and_version ${DPS_SERIAL_NUMBER}
send_online_state ${OVEN_SERIAL_NUMBER}
sleep 2

#echo "Sending factsheets"
send_factsheet_fts ${FTS_SERIAL_NUMBER}
send_factsheet_module ${DRILL_SERIAL_NUMBER} "DRILL" "false"
send_factsheet_module ${MILL_SERIAL_NUMBER} "MILL" "false"
send_factsheet_module ${HBW_SERIAL_NUMBER} "HBW" "true"
send_factsheet_module ${AIQS_SERIAL_NUMBER} "AIQS" "false" "calibrate"
send_factsheet_module ${DPS_SERIAL_NUMBER} "DPS" "true"
send_factsheet_module ${OVEN_SERIAL_NUMBER} "OVEN" "false"
sleep 2

#echo "Sending calibration state information"
send_calibration_state ${AIQS_SERIAL_NUMBER}
sleep 2

#echo "Sending current state information"
send_state_fts ${FTS_SERIAL_NUMBER} ${DPS_SERIAL_NUMBER}
send_state ${DRILL_SERIAL_NUMBER}
send_state ${MILL_SERIAL_NUMBER}
send_state ${HBW_SERIAL_NUMBER}
send_state ${AIQS_SERIAL_NUMBER}
send_state ${DPS_SERIAL_NUMBER}
send_state ${OVEN_SERIAL_NUMBER}
sleep 2

#echo "Sending error state information"
send_error_state ${DRILL_SERIAL_NUMBER} "PICK"
send_error_state ${MILL_SERIAL_NUMBER} "DROP"
send_error_state ${HBW_SERIAL_NUMBER} "PICK"
send_error_state ${AIQS_SERIAL_NUMBER} "DROP"
send_error_state ${DPS_SERIAL_NUMBER} "PICK"
send_error_state ${OVEN_SERIAL_NUMBER} "FIRE"
