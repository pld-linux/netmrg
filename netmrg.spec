Summary:	Network Monitoring package using PHP, MySQL, and RRDtool
Summary(pl):	Monitor sieci u¿ywaj±cy PHP, MySQL i RRDtool
Name:		netmrg
Version:	0.13
Release:	0.1
License:	MIT
Group:		Applications/Networking
Source0:	http://www.netmrg.net/download/release/%{name}-%{version}.tar.gz
# Source0-md5:	52dab94b707e08531baac3a8d4164ff5
Source1:	%{name}-httpd.conf
Source2:	%{name}-cron
Patch0:		%{name}-config.patch
URL:		http://www.netmrg.net/
BuildRequires:	mysql-devel
BuildRequires:	libxml2-devel
PreReq:		webserver
Requires:	libxml2
Requires:	rrdtool
Requires:	php-mysql
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir		/var/lib/%{name}
%define		_wwwuser		http
%define		_wwwgroup		http
%define		_wwwrootdir		/home/services/httpd

%description
NetMRG is a tool for network monitoring, reporting, and graphing.
Based on RRDTOOL, the best of open source graphing systems, NetMRG is
capable of creating graphs of any parameter of your network.

%description -l pl
NetMGR s³u¿y do monitorowania sieci, raportowania i kre¶lenia
wykresów.

%prep
%setup -q
%patch0 -p1

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} install DESTDIR=$RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_wwwrootdir}
install -D %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/httpd.conf/netrmg.conf
install -D %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/cron.d/netmrg
mv -f $RPM_BUILD_ROOT/var/www/netmrg $RPM_BUILD_ROOT%{_wwwrootdir}/netmrg
touch $RPM_BUILD_ROOT/var/log/netmrg/lastrun.err
touch $RPM_BUILD_ROOT/var/log/netmrg/lastrun.log
touch $RPM_BUILD_ROOT/var/log/netmrg/runtime

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi
echo "Before first run read /usr/share/doc/netmrg-0.13/INSTAL how to put
	/usr/share/netmrg/db/netmrg.mysql in your mysql server"


%preun
if [ "$1" = 0 ]
then
	if [ -f /var/lock/subsys/httpd ]; then
		/etc/rc.d/init.d/httpd restart 1>&2
	fi
fi

%files
%defattr(644,root,root,755)
%doc %{_docdir}/%{name}-%{version}
%{_mandir}/*/*
%attr(640,root,root) %{_sysconfdir}/cron.d/netmrg
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/netmrg.xml
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/httpd/httpd.conf/netrmg.conf
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/db
%dir %{_datadir}/%{name}/images
%{_datadir}/%{name}/*/*
%dir %{_wwwrootdir}/netmrg
%dir %{_wwwrootdir}/netmrg/include
%dir %{_wwwrootdir}/netmrg/lib
%dir %{_wwwrootdir}/netmrg/webfiles
%dir %{_wwwrootdir}/netmrg/webfiles/images
%dir %{_wwwrootdir}/netmrg/webfiles/images/default
%dir %{_wwwrootdir}/netmrg/webfiles/include
%dir %{_wwwrootdir}/netmrg/webfiles/img
%{_wwwrootdir}/netmrg/include/config.php
%{_wwwrootdir}/netmrg/*/*.php
%{_wwwrootdir}/netmrg/*/*.ico
%{_wwwrootdir}/netmrg/webfiles/images/default/*
%{_wwwrootdir}/netmrg/webfiles/img/*
%{_wwwrootdir}/netmrg/webfiles/include/netmrg.css
%dir %{_pkglibdir}
%attr(700,http,http) %dir %{_pkglibdir}/rrd
%attr(700,http,http) %{_pkglibdir}/rrd/*
%attr(770,http,http) %dir /var/log/netmrg
%attr(660,http,http) /var/log/netmrg/*
%attr(755,root,root) %{_bindir}/editrrd.pl
%attr(755,root,root) %{_bindir}/netmrg_cron.sh
%attr(755,root,root) %{_bindir}/netmrg-gatherer
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/*
