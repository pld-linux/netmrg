%define		snap	050727
Summary:	Network Monitoring package using PHP, MySQL, and RRDtool
Summary(pl):	Monitor sieci u¿ywaj±cy PHP, MySQL i RRDtool
Name:		netmrg
Version:	0.18.2
Release:	1.%{snap}.1
License:	MIT
Group:		Applications/Networking
#Source0:	http://www.netmrg.net/download/release/%{name}-%{version}.tar.gz
Source0:	http://mieszkancy.ds.pg.gda.pl/~luzik/%{name}-%{snap}.tar.gz
# Source0-md5:	e4baf3664aad402d6116fd3863a7d856
Source1:	%{name}-httpd.conf
Source2:	%{name}-cron
Patch0:		%{name}-config.patch
URL:		http://www.netmrg.net/
BuildRequires:	mysql-devel
BuildRequires:	libxml2-devel
BuildRequires:	rrdtool-devel
BuildRequires:	net-snmp-devel
PreReq:		webserver
Requires:	libxml2
Requires:	rrdtool
Requires:	php-mysql
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_pkglibdir		/var/lib/%{name}
%define		_wwwuser		http
%define		_wwwgroup		http
%define		_wwwrootdir		%{_datadir}/%{name}/webfiles

%description
NetMRG is a tool for network monitoring, reporting, and graphing.
Based on RRDTOOL, the best of open source graphing systems, NetMRG is
capable of creating graphs of any parameter of your network.

%description -l pl
NetMRG s³u¿y do monitorowania sieci, raportowania i kre¶lenia
wykresów. Jest on oparty na RRDTOOL, najlepszym spo¶ród systemów
graficznych o dostêpnym kodzie ¼ród³owym. NetMRG potrafi tworzyæ
wykresy przedstawiaj±ce dowolne parametry sieci.

%prep
%setup -q -n %{name}
%patch0 -p1

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_wwwrootdir}

%{__make} install DESTDIR=$RPM_BUILD_ROOT

install -D %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/%{name}.conf
install -D %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/cron.d/%{name}
mv -f $RPM_BUILD_ROOT/var/www/%{name} $RPM_BUILD_ROOT%{_wwwrootdir}/%{name}
touch $RPM_BUILD_ROOT/var/log/%{name}/lastrun.err
touch $RPM_BUILD_ROOT/var/log/%{name}/lastrun.log
touch $RPM_BUILD_ROOT/var/log/%{name}/runtime

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*%{name}.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/httpd/%{name}.conf" >> /etc/httpd/httpd.conf
elif [ -d /etc/httpd/httpd.conf ]; then
	mv -f /etc/httpd/%{name}.conf /etc/httpd/httpd.conf/99_%{name}.conf
fi
if [ -f /var/lock/subsys/httpd ]; then
	/etc/rc.d/init.d/httpd restart 1>&2
fi
if [ -f /var/lock/subsys/crond ]; then
	/etc/rc.d/init.d/crond restart 1>&2
fi
echo "Before first run read /usr/share/doc/%{name}-%{version}/INSTALL how to put
/usr/share/netmrg/db/netmrg.mysql in your mysql server"


%preun
if [ "$1" = "0" ]; then
	umask 027
	if [ -d /etc/httpd/httpd.conf ]; then
		rm -f /etc/httpd/httpd.conf/99_%{name}.conf
	else
		grep -v "^Include.*%{name}.conf" /etc/httpd/httpd.conf > \
			etc/httpd/httpd.conf.tmp
		mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
		if [ -f /var/lock/subsys/httpd ]; then
			/usr/sbin/apachectl restart 1>&2
		fi
	fi
fi

%files
%defattr(644,root,root,755)
%doc %{_docdir}/%{name}-%{version}
%attr(640,root,root) %{_sysconfdir}/cron.d/netmrg
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/netmrg.xml
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/httpd/%{name}.conf
%attr(755,root,root) %{_bindir}/netmrg-gatherer
%attr(755,root,root) %{_bindir}/rrdedit
%{_datadir}/%{name}
%dir %{_pkglibdir}
%attr(700,http,http) %dir %{_pkglibdir}/rrd
%attr(700,http,http) %{_pkglibdir}/rrd/*
%attr(770,http,http) %dir /var/log/netmrg
%attr(660,http,http) /var/log/netmrg/*
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/*
%{_mandir}/*/*
