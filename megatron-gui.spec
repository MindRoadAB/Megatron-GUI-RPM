Name:           megatron-gui
Version:        0.0.1
Release:        1%{?dist}
Summary:        Megatron GUI - A Web GUI for megatron
BuildArch:      noarch

License:        GPL
Source0:        %{name}-%{version}.tar.gz

Requires:       httpd
Requires:       python3
Requires:       python3-mod_wsgi
Requires:       python3-flask
Requires:       python3-PyMySQL
Requires:       python3-sqlalchemy

%description
A GUI for Megatron

%install
mkdir -p %{buildroot}/var/www/megatron-gui/api
mkdir -p %{buildroot}/var/www/megatron-gui/web

mkdir -p %{buildroot}/etc/httpd/conf.d

cp -rf dist/api/* %{buildroot}/var/www/megatron-gui/api/
cp -rf dist/web/* %{buildroot}/var/www/megatron-gui/web/

cp -f conf/api.wsgi %{buildroot}/var/www/megatron-gui/api/api.wsgi
cp -f conf/db.cfg %{buildroot}/var/www/megatron-gui/api/db.cfg
cp -f conf/megatron-gui.conf %{buildroot}/etc/httpd/conf.d/megatron-gui.conf

%post
setsebool -P httpd_can_network_connect on
systemctl restart httpd
systemctl enable httpd

firewall-cmd --zone=public --add-port=80/tcp --permanent
firewall-cmd --reload

%clean
rm -rf $RPM_BUILD_ROOT

%files
%attr(777, -, -) /var/www/megatron-gui/api
%attr(777, -, -) /var/www/megatron-gui/web
%attr(777, -, -) /var/www/megatron-gui/api/api.wsgi
%attr(777, -, -) /var/www/megatron-gui/api/db.cfg
%attr(777, -, -) /etc/httpd/conf.d/megatron-gui.conf

