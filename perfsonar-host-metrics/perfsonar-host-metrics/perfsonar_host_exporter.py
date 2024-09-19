#!/usr/bin/env python3

import argparse
import os
import requests
import subprocess
from psconfig.utilities.metrics import PSConfigMetricCalculator
from psconfig.utilities.cli import PSCONFIG_CLI_AGENTS
from flask import Flask, Response

app = Flask(__name__)

class PSMetricsWebHandler:
    LS_BASE_URL = "http://35.223.142.206:8090/lookup/records"

    def _read_one_liner(self, filename):
        value = ""
        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                for line in file:
                    value = line.rstrip('\n') 
                    if value: break
        return value

    def pscheduler_metrics(self):
        ##
        # Exec pscheduler metrics command
        ps_metric_output = ""
        try:
            result = subprocess.run(["pscheduler", "metrics", "--format", "prometheus"], text=True, capture_output=True)
            if result and result.returncode == 0 and result.stdout:
                ps_metric_output = result.stdout
        except:
            # probably not installed, so ignore
            pass

        return ps_metric_output

    def psconfig_metrics(self):
        # Find agent
        ps_metric_output = ""
        for psconfig_agent in PSCONFIG_CLI_AGENTS:
            #Try each agent, but don't exit if exception since agent may not be installed
            try:
                # Get metrics
                agent_name = psconfig_agent["name"].lower()
                psconfig_calculator = PSConfigMetricCalculator(agent_name)
                psconfig_metrics = psconfig_calculator.run_metrics()
                if psconfig_metrics.guid:
                    ps_metric_output += psconfig_metrics.to_prometheus()
                # Get remotes
                config = psconfig_agent["client_class"](url=psconfig_agent["config_file"]).get_config()
                remote_fmt = 'perfsonar_psconfig_{}_remote{{url="{}",configure_archives="{}"}} 1\n'
                if config.remotes():
                    ps_metric_output += "# HELP perfsonar_psconfig_{0}_remote Information about pSConfig {0} agent remote configurations\n".format(agent_name)
                    ps_metric_output += "# TYPE perfsonar_psconfig_{0}_remote gauge\n".format(agent_name)
                    for remote in config.remotes():
                        ps_metric_output += remote_fmt.format(agent_name, remote.url(), remote.configure_archives())
                # Get agent uuid
                if agent_name == "pscheduler":
                    uuid_file = config.client_uuid_file()
                    if not uuid_file:
                        uuid_file = "/var/lib/perfsonar/psconfig/client_uuid"
                    uuid = self._read_one_liner(uuid_file)
                    if uuid:
                        ps_metric_output += "# HELP perfsonar_psconfig_{0}_agent Information about the pSConfig {0} agent\n".format(agent_name)
                        ps_metric_output += "# TYPE perfsonar_psconfig_{0}_agent gauge\n".format(agent_name)
                        ps_metric_output += 'perfsonar_psconfig_{}_agent{{client_uuid="{}"}} 1\n'.format(agent_name, uuid)
            except:
                pass

        return ps_metric_output

    def bundle_metrics(self):
        ##
        # Get bundle type and version
        bundle_type = self._read_one_liner("/var/lib/perfsonar/bundles/bundle_type")
        bundle_version = self._read_one_liner("/var/lib/perfsonar/bundles/bundle_version")
        
        ##
        # Output prometheus if we at least have type
        ps_metric_output = ""
        if bundle_type:
            ps_metric_output = "# HELP perfsonar_bundle Information about perfSONAR bundle installed\n"
            ps_metric_output += "# TYPE perfsonar_bundle gauge\n"
            ps_metric_output += 'perfsonar_bundle{{type="{}",version="{}"}} 1\n'.format(bundle_type, bundle_version)
        
        return ps_metric_output

    def _is_registered(self, uuid):
        ls_url = "{}?type=host&client-uuid={}".format(self.LS_BASE_URL, uuid)
        try:
            r = requests.get(ls_url, timeout=3)
            r.raise_for_status()
            if r and r.json() and r.json()[0].get("client-uuid", None):
                return 1
        except:
            pass
        
        return 0

    def lookup_svc_metrics(self):
        ps_metric_output = ""

        ##
        # Get client uuid
        uuid = self._read_one_liner("/var/lib/perfsonar/lsregistrationdaemon/client_uuid")
        if uuid:
            ##
            # Test if registered
            ps_metric_output += "# HELP perfsonar_host_registered Indicates if perfSONAR host is registered in Lookup Service\n"
            ps_metric_output += "# TYPE perfsonar_host_registered gauge\n"
            ps_metric_output += 'perfsonar_host_registered{{uuid="{}"}} {}\n'.format(uuid, self._is_registered(uuid))

        return ps_metric_output
    
    def gather_metrics(self):
        ps_metric_output = ""
        # toolkit/bundle metrics
        ps_metric_output += self.bundle_metrics()
        # pScheduler metrics
        ps_metric_output += self.pscheduler_metrics()
        # pSConfig Metrics
        ps_metric_output += self.psconfig_metrics()
        # LS client uuid
        ps_metric_output += self.lookup_svc_metrics()
        return ps_metric_output

@app.route("/")
def metrics():
    handler = PSMetricsWebHandler()
    metrics_data = handler.gather_metrics()
    return Response(metrics_data, status=200, mimetype="text/plain")

if __name__ == "__main__":
    ##
    # Parse cli arguments
    parser = argparse.ArgumentParser(
        prog='perfsonar_exporter',
        description='A web server that exports metrics about a perfSONAR host in Prometheus format'
    )
    parser.add_argument('--host', dest='host', action='store', default='localhost', help='The host to listen for connections. 0.0.0.0 means all interfaces.')
    parser.add_argument('--port', dest='port', action='store', type=int, default=11284, help='The port on which to listen for connections.')
    args = parser.parse_args()

    app.run(host=args.host, port=args.port)