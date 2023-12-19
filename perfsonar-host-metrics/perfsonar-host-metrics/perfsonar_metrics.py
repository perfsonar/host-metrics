#!/usr/bin/env python3

from psconfig.utilities.metrics import PSConfigMetricCalculator
from psconfig.utilities.cli import PSCONFIG_CLI_AGENTS

##
# pSConfig Metrics
for psconfig_agent in PSCONFIG_CLI_AGENTS:
    #Try each agent, but don't exit if exception since agent may not be installed
    try:
        psconfig_calculator = PSConfigMetricCalculator(psconfig_agent["name"].lower())
        psconfig_metrics = psconfig_calculator.run_metrics()
        if psconfig_metrics.guid:
            print(psconfig_metrics.to_prometheus())
    except:
        pass
