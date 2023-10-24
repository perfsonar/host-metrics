%define install_base        /usr/lib/perfsonar
%define pkg_install_base    %{install_base}/host_metrics
%define httpd_config_base   /etc/httpd/conf.d

#Version variables set by automated scripts
%define perfsonar_auto_version 5.0.5
%define perfsonar_auto_relnum 1

# defining macros needed by SELinux
# SELinux policy type - Targeted policy is the default SELinux policy used in Red Hat Enterprise Linux.
%global selinuxtype targeted
# default boolean value needs to be changed to enable http proxy
%global selinuxbooleans httpd_can_network_connect=1

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
Requires:       httpd
Requires:       mod_ssl
Requires:       selinux-policy-%{selinuxtype}
Requires(post): selinux-policy-%{selinuxtype}
BuildRequires:  selinux-policy-devel
%{?selinux_requires}

%description
A package that installs and sets-up Prometheus node_exporter for a perfSONAR install

%prep
%setup -q -n perfsonar-host-metrics-%{version}

%build

%install
make PERFSONAR-ROOTPATH=%{buildroot}/%{pkg_install_base} HTTPD-CONFIGPATH=%{buildroot}/%{httpd_config_base} install

%clean
rm -rf %{buildroot}

%post
#Restart/enable opensearch and logstash
%systemd_post node_exporter.service
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
    #Enable and restart apache for reverse proxy
    systemctl enable httpd
    systemctl restart httpd
fi

%preun
%systemd_preun node_exporter.service

%postun
%systemd_postun_with_restart node_exporter.service
if [ $1 -eq 0 ]; then
    %selinux_unset_booleans -s %{selinuxtype} %{selinuxbooleans}
fi

%files
%defattr(0644,perfsonar,perfsonar,0755)
%license LICENSE
%attr(0755, perfsonar, perfsonar) %{pkg_install_base}/exporter_opts.sh
%attr(0644, perfsonar, perfsonar) %{httpd_config_base}/apache-node_exporter.conf

%changelog
* Tue Oct 24 2023 andy@es.net 5.0.5-0.0.a1
- Initial package