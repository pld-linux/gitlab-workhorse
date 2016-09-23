Summary:	An HTTP daemon that serves Git clients
Name:		gitlab-workhorse
Version:	0.8.2
Release:	1
License:	MIT
Group:		Development/Building
Source0:	https://gitlab.com/gitlab-org/gitlab-workhorse/repository/archive.tar.gz?ref=v%{version}&/%{name}-%{version}.tar.gz
# Source0-md5:	4f5a2b358a6e6c51216323459fd8854d
Source1:	%{name}.service
Source2:	%{name}.init
URL:		https://gitlab.com/gitlab-org/gitlab-workhorse
BuildRequires:	git-core
BuildRequires:	golang >= 1.5
BuildRequires:	rpmbuild(macros) >= 1.647
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts >= 0.4.16
Requires:	systemd-units >= 0.38
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
install -d $RPM_BUILD_ROOT{%{_sbindir},%{systemdunitdir},/etc/rc.d/init.d}

install -p %{name} $RPM_BUILD_ROOT%{_sbindir}/%{name}
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service
cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
%service %{name} restart
%systemd_post %{name}.service

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi
%systemd_preun %{name}.service

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%doc CHANGELOG README.md LICENSE
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_sbindir}/%{name}
%{systemdunitdir}/%{name}.service
