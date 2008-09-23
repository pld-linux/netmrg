# TODO
#	- lighttpd config file (and webapp trigger)
#	- create netmrg user/group to run as
#	- cron/standalone subpackages
#	- logrotate file
Summary:	Network Monitoring package using PHP, MySQL, and RRDtool
Summary(pl.UTF-8):	Monitor sieci używający PHP, MySQL i RRDtool
Name:		netmrg
Version:	0.20
Release:	1
License:	MIT
Group:		Applications/Networking
Source0:	http://www.netmrg.net/download/release/%{name}-%{version}.tar.gz
# Source0-md5:	a380390425f8f97cadaee3809042ca51
Source1:	%{name}-httpd.conf
Source2:	%{name}-cron
Patch0:		%{name}-config.patch
Patch1:		%{name}-bashizm.patch
URL:		http://www.netmrg.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libstdc++-devel
BuildRequires:	libxml2-devel
BuildRequires:	mysql-devel
BuildRequires:	net-snmp-devel
BuildRequires:	rpmbuild(macros) >= 1.268
BuildRequires:	rrdtool-devel >= 1.2.10
BuildRequires:	sed >= 4.0
Requires:	libxml2
Requires:	php(mysql)
Requires:	rrdtool >= 1.2.10
Requires:	webserver
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_appdir			%{_datadir}/%{name}
%define		_pkglibdir		/var/lib/%{name}
%define		_webapps		/etc/webapps
%define		_webapp			%{name}
%define		_sysconfdir		%{_webapps}/%{_webapp}

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
%patch1 -p0

%build
install /usr/share/automake/config.* .
%{__gettextize}
%{__libtoolize}
%{__aclocal} -I m4
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	--with-snmp-lib-dir=%{_libdir} \
	--with-www-dir=%{_appdir}
%{__make}
sed -i -e '1s|^#!/usr/bin/php |#!/usr/bin/php.cli |' libexec/*.php

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/cron.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install www/include/config_site-dist.php $RPM_BUILD_ROOT%{_sysconfdir}/config_site.php
ln -s %{_sysconfdir}/config_site.php $RPM_BUILD_ROOT%{_appdir}/include
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/apache.conf
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/httpd.conf
install %{SOURCE2} $RPM_BUILD_ROOT/etc/cron.d/%{name}
rm -rf $RPM_BUILD_ROOT{%{_sysconfdir}/netmrg.conf,%{_bindir}/rrdedit,%{_appdir}/{contrib,db}}
:> $RPM_BUILD_ROOT/var/log/%{name}/lastrun.err
:> $RPM_BUILD_ROOT/var/log/%{name}/lastrun.log
:> $RPM_BUILD_ROOT/var/log/%{name}/runtime

%clean
rm -rf $RPM_BUILD_ROOT

%triggerin -- apache1 < 1.3.37-3, apache1-base
%webapp_register apache %{_webapp}

%triggerun -- apache1 < 1.3.37-3, apache1-base
%webapp_unregister apache %{_webapp}

%triggerin -- apache < 2.2.0, apache-base
%webapp_register httpd %{_webapp}

%triggerun -- apache < 2.2.0, apache-base
%webapp_unregister httpd %{_webapp}

%triggerpostun -- netmrg < 0.20
# rescue app config from old location (with old paths, but good MySQL password)
if [ -f /etc/netmrg.xml.rpmsave ]; then
	mv -f %{_sysconfdir}/netmrg.xml{,.rpmnew}
	mv -f /etc/netmrg.xml.rpmsave %{_sysconfdir}/netmrg.xml
fi

# nuke very-old config location (this mostly for Ra)
if [ -f /etc/httpd/httpd.conf ]; then
	sed -i -e "/^Include.*%{name}.conf/d" /etc/httpd/httpd.conf
	httpd_reload=1
fi

# migrate from httpd (apache2) config dir
if [ -f /etc/httpd/%{name}.conf.rpmsave ]; then
	mv -f %{_sysconfdir}/httpd.conf{,.rpmnew}
	mv -f /etc/httpd/%{name}.conf.rpmsave %{_sysconfdir}/httpd.conf
	httpd_reload=1
fi
if [ -f /etc/httpd/httpd.conf/99_%{name}.conf ]; then
	mv -f %{_sysconfdir}/httpd.conf{,.rpmnew}
	mv -f /etc/httpd/httpd.conf/99_%{name}.conf %{_sysconfdir}/httpd.conf
fi

if [ -d /etc/httpd/webapps.d ]; then
	/usr/sbin/webapp register httpd %{_webapp}
	httpd_reload=1
fi

[ -n "$httpd_reload" ] && %service -q httpd reload

%post
%service crond restart

if [ "$1" = 1 ]; then
	%banner -e %{name} << EOF
	You must create MySQL database for NetMRG. Running these should be fine in most cases:
	mysqladmin create netmrg
	zcat %{_docdir}/%{name}-%{version}/netmrg.mysql.gz | mysql -u mysql -p netmrg
	mysql -u mysql -p
> grant all on netmrg.* to netmrguser@localhost identified by 'netmrgpass';
EOF
fi

%files
%defattr(644,root,root,755)
%doc bin/rrdedit contrib etc/init.d-netmrg libexec/linuxload.sh libexec/snmpdiff.sh
%doc share/doc/html share/doc/txt/netmrg.txt share/doc/ChangeLog share/doc/TODO share/doc/VERSION share/doc/netmrg.sgml share/doc/rrdworld.xml
%doc share/netmrg.mysql README RELEASE-NOTES UPGRADE
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/cron.d/%{name}
%attr(750,root,http) %dir %{_sysconfdir}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/*.conf
%attr(644,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/config_site.php
%attr(640,root,http) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/netmrg.xml
%attr(755,root,root) %{_bindir}/netmrg-gatherer
%{_appdir}
%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/*
%dir %{_pkglibdir}
%attr(770,root,http) %dir %{_pkglibdir}/rrd
%attr(660,root,http) %{_pkglibdir}/rrd/*
%attr(770,root,http) %dir /var/log/netmrg
%attr(660,root,http) %verify(not md5 mtime size) /var/log/netmrg/*
%{_mandir}/*/*
