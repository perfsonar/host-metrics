#
# WSGI File for host_exporter
#
import sys

sys.path.insert(0, '/var/www/html/perfsonar/host_exporter')

from host_exporter.perfsonar_host_exporter import app as application
