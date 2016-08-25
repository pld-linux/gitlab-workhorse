Summary:	An HTTP daemon that serves Git clients
Name:		gitlab-workhorse
Version:	0.7.11
Release:	0.7
License:	MIT
Group:		Development/Building
# md5 deliberately omitted until this package is useful
Source0:	https://gitlab.com/gitlab-org/gitlab-workhorse/repository/archive.tar.gz?ref=v%{version}&/%{name}-%{version}.tar.gz
Source1:	%{name}.service
URL:		https://gitlab.com/gitlab-org/gitlab-workhorse
BuildRequires:	git-core
BuildRequires:	golang >= 1.6
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
# make version similar when built from git:
# Starting gitlab-workhorse v0.7.1-20160404.102052
version=v%{version}-$(date -u +%%Y%%m%%d.%%H%%M%%S)

%{__make} \
	VERSION=$version

# verify
./gitlab-workhorse --version > v
grep "$version" v

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sbindir},%{systemdunitdir}}

install -p %{name} $RPM_BUILD_ROOT%{_sbindir}/%{name}
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service

%clean
rm -rf $RPM_BUILD_ROOT

%preun
%systemd_preun %{name}.service

%post
%systemd_post %{name}.service

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%doc CHANGELOG README.md LICENSE
%attr(755,root,root) %{_sbindir}/%{name}
%{systemdunitdir}/%{name}.service
