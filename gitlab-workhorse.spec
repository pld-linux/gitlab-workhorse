Summary:	Handles slow HTTP requests for GitLab
Name:		gitlab-workhorse
Version:	3.3.1
Release:	1
License:	MIT
Group:		Networking/Daemons/HTTP
Source0:	https://gitlab.com/gitlab-org/gitlab-workhorse/repository/archive.tar.bz2?ref=v%{version}&/%{name}-%{version}.tar.bz2
# Source0-md5:	5e8c97210890028d440b5da19f95d5ad
Source1:	%{name}.service
Source2:	%{name}.init
Source3:	%{name}.sysconfig
Patch0:		paths.patch
URL:		https://gitlab.com/gitlab-org/gitlab-workhorse
BuildRequires:	git-core
BuildRequires:	golang >= 1.8
BuildRequires:	rpmbuild(macros) >= 1.647
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts >= 0.4.16
Requires:	systemd-units >= 0.38
Obsoletes:	gitlab-git-http-server <= 0.3.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Gitlab-workhorse is a smart reverse proxy for GitLab. It handles
"large" HTTP requests such as file downloads, file uploads, Git
push/pull and Git archive downloads.

%prep
%setup -qc
mv %{name}-v%{version}-*/* .
%patch0 -p1

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
install -d $RPM_BUILD_ROOT{%{systemdunitdir},/etc/{rc.d/init.d,sysconfig}}

%{__make} install \
	PREFIX=%{_prefix} \
	DESTDIR=$RPM_BUILD_ROOT

cp -p %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service
install -p %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -p %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

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
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(755,root,root) %{_sbindir}/gitlab-workhorse
%attr(755,root,root) %{_sbindir}/gitlab-zip-cat
%attr(755,root,root) %{_sbindir}/gitlab-zip-metadata
%{systemdunitdir}/%{name}.service
