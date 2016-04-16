#
# Conditional build:
%bcond_with systemd

Summary:	An HTTP daemon that serves Git clients
Name:		gitlab-workhorse
Version:	0.7.1
Release:	0.2
License:	MIT
Group:		Development/Building
# md5 deliberately omitted until this package is useful
Source0:	https://gitlab.com/gitlab-org/gitlab-workhorse/repository/archive.tar.gz?ref=v%{version}&/%{name}-%{version}.tar.gz
Source1:	%{name}.service
URL:		https://gitlab.com/gitlab-org/gitlab-workhorse
BuildRequires:	git-core
BuildRequires:	golang
%{?with_systemd:BuildRequires:	systemd-units}
Obsoletes:	gitlab-git-http-server <= 0.3.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
gitlab-git-http-server was designed to unload Git HTTP traffic from
the GitLab Rails app (Unicorn) to a separate daemon. All
authentication and authorization logic is still handled by the GitLab
Rails app.

%prep
%setup -qc
mv %{name}-v%{version}-*/* .

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -D %{name} $RPM_BUILD_ROOT%{_sbindir}/%{name}
%if %{with systemd}
install -D %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%if %{with systemd}
%preun
%systemd_preun %{name}.service

%post
%systemd_post %{name}.service

%postun
%systemd_postun_with_restart %{name}.service
%endif

%files
%defattr(644,root,root,755)
%doc CHANGELOG README.md LICENSE
%attr(755,root,root) %{_sbindir}/%{name}
%if %{with systemd}
%{systemdunitdir}/%{name}.service
%endif
