# TODO
# - use webapps
# warning: Installed (but unpackaged) file(s) found:
#   /etc/netmrg.conf
Summary:	Network Monitoring package using PHP, MySQL, and RRDtool
Summary(pl.UTF-8):	Monitor sieci używający PHP, MySQL i RRDtool
Name:		netmrg
Version:	0.19
Release:	3
License:	MIT
Group:		Applications/Networking
Source0:	http://www.netmrg.net/download/devel/%{name}-%{version}.tar.gz
# Source0-md5:	a380390425f8f97cadaee3809042ca51
Source1:	%{name}-httpd.conf
Source2:	%{name}-cron
Patch0:		%{name}-config.patch
URL:		http://www.netmrg.net/
BuildRequires:	automake
BuildRequires:	libxml2-devel
BuildRequires:	mysql-devel
BuildRequires:	net-snmp-devel
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	rrdtool-devel >= 1.2.10
Requires:	libxml2
Requires:	php(mysql)
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

%description -l pl.UTF-8
NetMRG służy do monitorowania sieci, raportowania i kreślenia
wykresów. Jest on oparty na RRDTOOL, najlepszym spośród systemów
graficznych o dostępnym kodzie źródłowym. NetMRG potrafi tworzyć
wykresy przedstawiające dowolne parametry sieci.

%prep
%setup -q
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

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -f /etc/httpd/httpd.conf ] && ! grep -q "^Include.*%{name}.conf" /etc/httpd/httpd.conf; then
	echo "Include /etc/httpd/%{name}.conf" >> /etc/httpd/httpd.conf
elif [ -d /etc/httpd/httpd.conf ]; then
	mv -f /etc/httpd/%{name}.conf /etc/httpd/httpd.conf/99_%{name}.conf
fi
%service httpd reload
%service crond restart
if [ -f /var/lock/subsys/crond ]; then
	/etc/rc.d/init.d/crond restart 1>&2
fi
echo "Before first run read %{_docdir}/%{name}-%{version}/INSTALL how to put
%{_datadir}/netmrg/db/netmrg.mysql in your mysql server"

%preun
if [ "$1" = "0" ]; then
	umask 027
	if [ -d /etc/httpd/httpd.conf ]; then
		rm -f /etc/httpd/httpd.conf/99_%{name}.conf
	else
		grep -v "^Include.*%{name}.conf" /etc/httpd/httpd.conf > \
			etc/httpd/httpd.conf.tmp
		mv -f /etc/httpd/httpd.conf.tmp /etc/httpd/httpd.conf
		%service httpd reload
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
%attr(770,root,http) %dir %{_pkglibdir}/rrd
%attr(770,root,http) %{_pkglibdir}/rrd/*
%attr(770,root,http) %dir /var/log/netmrg
%attr(660,root,http) /var/log/netmrg/*
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/*
%{_mandir}/*/*
