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


%description
Prometheus exporter for hardware and OS metrics exposed by *NIX kernels,
written in Go with pluggable metric collectors.



%prep
%setup -q


%build
make install


%install
mkdir -vp %{buildroot}%{_sharedstatedir}/prometheus
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
%systemd_post %{service_name}.service


%preun
%systemd_preun %{service_name}.service


%postun
%systemd_postun %{service_name}.service


%files
%defattr(-,root,root,-)
%{_bindir}/%{service_name}
%config(noreplace) %{_sysconfdir}/default/%{service_name}
%dir %attr(755, %{user}, %{group}) %{_sharedstatedir}/prometheus
%{_unitdir}/%{service_name}.service

