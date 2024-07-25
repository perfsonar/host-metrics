%define install_base        /usr/lib/perfsonar
%define pkg_install_base    %{install_base}/host_metrics
%define httpd_config_base   /etc/httpd/conf.d

#Version variables set by automated scripts
%define perfsonar_auto_version 5.1.3
%define perfsonar_auto_relnum 0.a1.0

# defining macros needed by SELinux
# SELinux policy type - Targeted policy is the default SELinux policy used in Red Hat Enterprise Linux.
%global selinuxtype targeted
# default boolean value needs to be changed to enable http proxy
%global selinuxbooleans httpd_can_network_connect=1

#
# Python
#

# This is the version we like.
%define _python_version_major 3

%if 0%{?el7}
%error EL7 is no longer supported.  Try something newer.
%endif

%if 0%{?el8}%{?ol8}
# EL8 standardized on just the major version, as did EPEL.
%define _python python%{_python_version_major}

%else

# EL9+ has everyting as just plain python
%define _python python

%endif

Name:			perfsonar-host-metrics
Version:		%{perfsonar_auto_version}
Release:		%{perfsonar_auto_relnum}%{?dist}
Summary:		perfSONAR Host Metrics
License:		ASL 2.0
Group:			Development/Libraries
URL:			http://www.perfsonar.net
Source0:		perfsonar-host-metrics-%{version}.tar.gz
BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:		noarch

Requires:       perfsonar-common
Requires:       openssl
Requires:       prometheus-node-exporter
Requires:       %{_python}-perfsonar-psconfig
Requires:       %{_python}-pscheduler
Requires:       %{_python}-requests
Requires:       httpd
Requires:       mod_ssl
Requires:       selinux-policy-%{selinuxtype}
Requires(post): selinux-policy-%{selinuxtype}
BuildRequires:  selinux-policy-devel
Requires:       policycoreutils, libselinux-utils
Requires(post): policycoreutils
Requires(postun): policycoreutils

%{?selinux_requires}

%description
A package that installs and sets-up Prometheus node_exporter for a perfSONAR install

%prep
%setup -q -n perfsonar-host-metrics-%{version}

%build
make -f /usr/share/selinux/devel/Makefile -C selinux perfsonar_host_metrics.pp

%install
make PERFSONAR-ROOTPATH=%{buildroot}/%{pkg_install_base} HTTPD-CONFIGPATH=%{buildroot}/%{httpd_config_base} install
mkdir -p %{buildroot}/%{_unitdir}/
install -m 644 *.service %{buildroot}/%{_unitdir}/
mkdir -p %{buildroot}/usr/share/selinux/packages/
mv selinux/*.pp %{buildroot}/usr/share/selinux/packages/

%clean
rm -rf %{buildroot}

%post

#selinux
semodule -n -i /usr/share/selinux/packages/perfsonar_host_metrics.pp
if /usr/sbin/selinuxenabled; then
    /usr/sbin/load_policy
fi

#Restart/enable opensearch and logstash
%systemd_post node_exporter.service
%systemd_post perfsonar-host-exporter.service
if [ "$1" = "1" ]; then
    #set SELinux booleans to allow httpd proxy to work
    %selinux_set_booleans -s %{selinuxtype} %{selinuxbooleans}
    #update node_exporter to monitor pS processes
    %{pkg_install_base}/exporter_opts.sh

    ######
    #if new install, then enable
    systemctl daemon-reload
    systemctl enable node_exporter.service
    systemctl restart node_exporter.service
    systemctl enable perfsonar-host-exporter.service
    systemctl restart perfsonar-host-exporter.service
    #Enable and restart apache for reverse proxy
    systemctl enable httpd
    systemctl restart httpd
else
    #update node_exporter to monitor pS processes
    %{pkg_install_base}/exporter_opts.sh
fi

%preun
%systemd_preun node_exporter.service
%systemd_preun perfsonar-host-exporter.service

%postun
%systemd_postun_with_restart node_exporter.service
%systemd_postun_with_restart perfsonar-host-exporter.service
if [ $1 -eq 0 ]; then
    %selinux_unset_booleans -s %{selinuxtype} %{selinuxbooleans}
    semodule -n -r perfsonar_host_metrics
    if /usr/sbin/selinuxenabled; then
       /usr/sbin/load_policy
    fi
fi

%files
%defattr(0644,perfsonar,perfsonar,0755)
%license LICENSE
%attr(0755, perfsonar, perfsonar) %{pkg_install_base}/exporter_opts.sh
%attr(0755, perfsonar, perfsonar) %{pkg_install_base}/perfsonar_host_exporter
%attr(0644, perfsonar, perfsonar) %{httpd_config_base}/apache-node_exporter.conf
%attr(0644, perfsonar, perfsonar) %{httpd_config_base}/apache-perfsonar_host_exporter.conf
%attr(0644,root,root) /usr/share/selinux/packages/*
%{_unitdir}/perfsonar-host-exporter.service

%changelog
* Tue Oct 24 2023 andy@es.net 5.0.5-0.0.a1
- Initial package
