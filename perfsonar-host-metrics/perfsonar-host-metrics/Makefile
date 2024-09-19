# Makefile for perfSONAR Host Metrics
#
default:
	@true

install:
ifndef PERFSONAR-ROOTPATH
	@echo No PERFSONAR-ROOTPATH specified for installation
	@false
endif
ifndef HTTPD-CONFIGPATH
	@echo No HTTPD-CONFIGPATH specified for installation
	@false
endif
ifndef WSGI-CONFIGPATH
	@echo No WSGI-CONFIGPATH specified for installation
	@false
endif
	mkdir -p ${PERFSONAR-ROOTPATH}
	mkdir -p ${HTTPD-CONFIGPATH}
	mkdir -p ${WSGI-CONFIGPATH}
	install -m 755 exporter_opts.sh ${PERFSONAR-ROOTPATH}/
	install -m 755 perfsonar_host_exporter.py ${PERFSONAR-ROOTPATH}/
	install -m 644 apache-node_exporter.conf ${HTTPD-CONFIGPATH}/
	install -m 644 apache-perfsonar_host_exporter.conf ${HTTPD-CONFIGPATH}/
	install -m 644 host_exporter.wsgi ${WSGI-CONFIGPATH}/

clean:
	@true

