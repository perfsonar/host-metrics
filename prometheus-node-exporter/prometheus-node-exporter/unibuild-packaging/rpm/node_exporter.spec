%global debug_package %{nil}
%global user prometheus
%global group prometheus
%global service_name node_exporter

Name:    prometheus-node-exporter
Version: 1.6.1
Release: 1%{?dist}
Summary: Prometheus exporter for machine metrics, written in Go with pluggable metric collectors.
License: ASL 2.0
URL:     https://github.com/prometheus/node_exporter
Source0: %{name}-%{version}.tar.gz
# This is what Prometheus calls package, but inconsistent with deb naming rules
# so name it prometheus-node-exporter and use Provides so unibuild can build
Provides: %{service_name}

%if 0%{?fedora} >= 19
BuildRequires: systemd-rpm-macros
%endif
%{?systemd_requires}
Requires(pre): shadow-utils
# SELinux support
BuildRequires: selinux-policy-devel
Requires: policycoreutils, libselinux-utils
Requires(post): selinux-policy-targeted, policycoreutils
Requires(postun): policycoreutils

%description
Prometheus exporter for hardware and OS metrics exposed by *NIX kernels,
written in Go with pluggable metric collectors.



%prep
%setup -q


%build
make install
make -f /usr/share/selinux/devel/Makefile -C selinux node_exporter.pp


%install
mkdir -vp %{buildroot}%{_sharedstatedir}/prometheus
mkdir -p %{buildroot}/usr/share/selinux/packages/
mv selinux/*.pp %{buildroot}/usr/share/selinux/packages/
rm -rf %{buildroot}/usr/lib/perfsonar/selinux
install -D -m 755 bin/%{service_name} %{buildroot}%{_bindir}/%{service_name}
install -D -m 644 etc/default/%{service_name} %{buildroot}%{_sysconfdir}/default/%{service_name}
install -D -m 644 %{service_name}.service %{buildroot}%{_unitdir}/%{service_name}.service

%pre
getent group prometheus >/dev/null || groupadd -r prometheus
getent passwd prometheus >/dev/null || \
  useradd -r -g prometheus -d %{_sharedstatedir}/prometheus -s /sbin/nologin \
          -c "Prometheus services" prometheus
exit 0


%post
#Enable selinux
semodule -n -i /usr/share/selinux/packages/node_exporter.pp
if /usr/sbin/selinuxenabled; then
    /usr/sbin/load_policy
fi
%systemd_post %{service_name}.service


%preun
%systemd_preun %{service_name}.service


%postun
%systemd_postun %{service_name}.service
if [ $1 -eq 0 ]; then
    semodule -n -r node_exporter
    if /usr/sbin/selinuxenabled; then
       /usr/sbin/load_policy
    fi
fi

%files
%defattr(-,root,root,-)
%{_bindir}/%{service_name}
%config(noreplace) %{_sysconfdir}/default/%{service_name}
%dir %attr(755, %{user}, %{group}) %{_sharedstatedir}/prometheus
%{_unitdir}/%{service_name}.service
%attr(0644,root,root) %{_datadir}/selinux/packages/node_exporter.pp

