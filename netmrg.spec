%define		snap	051123
%define		snapd	2005.11.23
Summary:	Network Monitoring package using PHP, MySQL, and RRDtool
Summary(pl):	Monitor sieci u�ywaj�cy PHP, MySQL i RRDtool
Name:		netmrg
Version:	0.18.2
Release:	1.%{snap}.3
License:	MIT
Group:		Applications/Networking
#Source0:	http://www.netmrg.net/download/release/%{name}-%{version}.tar.gz
Source0:	http://www.netmrg.net/download/snapshot/%{name}-%{snapd}.tar.gz
# Source0-md5:	f122132e76cbe10e259bcd8fc4ab84d0
Source1:	%{name}-httpd.conf
Source2:	%{name}-cron
Patch0:		%{name}-config.patch
URL:		http://www.netmrg.net/
BuildRequires:	automake
BuildRequires:	libxml2-devel
BuildRequires:	mysql-devel
BuildRequires:	net-snmp-devel
BuildRequires:	rrdtool-devel >= 1.2.10
Requires:	libxml2
Requires:	php-mysql
Requires:	rrdtool >= 1.2.10
Requires:	webserver
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
NetMRG s�u�y do monitorowania sieci, raportowania i kre�lenia
wykres�w. Jest on oparty na RRDTOOL, najlepszym spo�r�d system�w
graficznych o dost�pnym kodzie �r�d�owym. NetMRG potrafi tworzy�
wykresy przedstawiaj�ce dowolne parametry sieci.

%prep
%setup -q -n %{name}-%{snapd}
%patch0 -p1

%build
install /usr/share/automake/config.* .
%{__gettextize}
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--with-snmp-lib-dir=%{_libdir}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_wwwrootdir}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -D %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd/%{name}.conf
install -D %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/cron.d/%{name}
mv -f $RPM_BUILD_ROOT/var/www/%{name} $RPM_BUILD_ROOT%{_wwwrootdir}/%{name}
touch $RPM_BUILD_ROOT/var/log/%{name}/lastrun.err
touch $RPM_BUILD_ROOT/var/log/%{name}/lastrun.log
touch $RPM_BUILD_ROOT/var/log/%{name}/runtime
mv $RPM_BUILD_ROOT%{_docdir}/netmrg-0.19cvs $RPM_BUILD_ROOT%{_docdir}/netmrg-%{version}

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
%attr(640,root,root) /etc/cron.d/netmrg
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/netmrg.xml
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/httpd/%{name}.conf
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
