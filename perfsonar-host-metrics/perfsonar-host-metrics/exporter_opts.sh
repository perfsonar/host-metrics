#!/bin/bash

TARGET_FILE="/etc/default/node_exporter"
EDIT_MARKER='#Edited by PS_HOST_METRICS'
NODE_EXPORTER_OPTS='PS_NODE_EXPORTER_OPTS=""'
grep -q PS_HOST_METRICS ${TARGET_FILE}
if [ $? -eq 1 ]; then
    TEMPFILE=$(mktemp)
    echo ${EDIT_MARKER} | cat - ${TARGET_FILE} > ${TEMPFILE}
    sed -E 's/^NODE_EXPORTER_OPTS="(.*)"/NODE_EXPORTER_OPTS="\1 --collector.systemd --collector.systemd.unit-include=^(elmond|grafana-server|httpd|logstash|node_exporter|opensearch-dashboards|opensearch|owamp|(perfsonar-.+)|postgresql|(pscheduler-.+)|(psconfig-.+))\.service"/' -i ${TEMPFILE}
    mv ${TEMPFILE} ${TARGET_FILE}
fi 
