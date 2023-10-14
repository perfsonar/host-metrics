#!/bin/bash

TARGET_FILE="/etc/default/node_exporter"
NODE_EXPORTER_OPTS='PS_NODE_EXPORTER_OPTS="--collector.systemd --collector.systemd.unit-include=^(elmond|grafana-server|httpd|logstash|node_exporter|opensearch-dashboards|opensearch|owamp|(perfsonar-.+)|postgresql|(pscheduler-.+)|(psconfig-.+))\.service"'
grep -q PS_NODE_EXPORTER_OPTS ${TARGET_FILE}
if [ $? -eq 1 ]; then
    TEMPFILE=$(mktemp)
    echo ${NODE_EXPORTER_OPTS} | cat - ${TARGET_FILE} > ${TEMPFILE}
    sed -E 's/^NODE_EXPORTER_OPTS="(.*)"/NODE_EXPORTER_OPTS="\1 \$PS_NODE_EXPORTER_OPTS"/' -i ${TEMPFILE}
    mv ${TEMPFILE} ${TARGET_FILE}
fi 
