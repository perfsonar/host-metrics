#!/bin/bash

TARGET_FILE="/etc/default/node_exporter"
EDIT_MARKER='#Edited by PS_HOST_METRICS'
grep -q PS_HOST_METRICS ${TARGET_FILE}
if [ $? -eq 1 ]; then
    TEMPFILE=$(mktemp)
    echo ${EDIT_MARKER} > ${TEMPFILE}
    OPTS="--collector.sysctl"
    OPTS="${OPTS} --collector.sysctl.include=net.core.rmem_max"
    OPTS="${OPTS} --collector.sysctl.include=net.core.rmem_default"
    OPTS="${OPTS} --collector.sysctl.include=net.core.wmem_max"
    OPTS="${OPTS} --collector.sysctl.include=net.core.wmem_default"
    OPTS="${OPTS} --collector.sysctl.include=net.ipv4.tcp_rmem:min,default,max"
    OPTS="${OPTS} --collector.sysctl.include=net.ipv4.tcp_wmem:min,default,max"
    OPTS="${OPTS} --collector.sysctl.include=net.ipv4.tcp_no_metrics_save"
    OPTS="${OPTS} --collector.sysctl.include=net.ipv4.tcp_mtu_probing"
    OPTS="${OPTS} --collector.sysctl.include-info=net.core.default_qdisc"
    OPTS="${OPTS} --collector.sysctl.include-info=net.ipv4.tcp_congestion_control"
    OPTS="${OPTS} --collector.sysctl.include-info=net.ipv4.tcp_available_congestion_control"
    OPTS="${OPTS} --collector.sysctl.include-info=net.ipv4.tcp_allowed_congestion_control"
    OPTS="${OPTS} --collector.sysctl.include=net.ipv4.conf.all.arp_ignore"
    OPTS="${OPTS} --collector.sysctl.include=net.ipv4.conf.all.arp_announce"
    OPTS="${OPTS} --collector.sysctl.include=net.ipv4.conf.default.arp_filter"
    OPTS="${OPTS} --collector.sysctl.include=net.ipv4.conf.all.arp_filter"
    OPTS="${OPTS} --collector.sysctl.include=net.core.netdev_max_backlog"
    OPTS="${OPTS} --collector.systemd"
    OPTS="${OPTS} --collector.systemd.unit-include=^(elmond|grafana-server|httpd|logstash|node_exporter|opensearch-dashboards|opensearch|owamp|(perfsonar-.+)|postgresql|(pscheduler-.+)|(psconfig-.+))\.service"
    echo "NODE_EXPORTER_OPTS=\"${OPTS}\"" >> ${TEMPFILE}
    mv ${TEMPFILE} ${TARGET_FILE}
fi 
