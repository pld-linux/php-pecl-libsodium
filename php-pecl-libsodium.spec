#
# Conditional build:
%bcond_without	tests		# build without tests

%define	buildver   %(pkg-config --silence-errors --modversion libsodium 2>/dev/null || echo 65536)

%define		php_name	php%{?php_suffix}
%define		modname	libsodium
Summary:	Wrapper for the Sodium cryptographic library
Summary(pl.UTF-8):	Interfejs do biblioteki kryptograficznej Sodium
Name:		%{php_name}-pecl-%{modname}
Version:	1.0.7
Release:	2
License:	BSD
Group:		Development/Languages
Source0:	http://pecl.php.net/get/%{modname}-%{version}.tgz
# Source0-md5:	d8edb46a03268c45bfca7951d5e7c57a
URL:		http://pecl.php.net/package/libsodium
BuildRequires:	%{php_name}-devel >= 4:5.3
BuildRequires:	libsodium-devel >= 0.6.0
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.666
%if %{with tests}
BuildRequires:	%{php_name}-cli
BuildRequires:	%{php_name}-json
BuildRequires:	%{php_name}-pcre
%endif
Requires:	libsodium >= %{buildver}
%{?requires_php_extension}
Provides:	php(libsodium) = %{version}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A simple, low-level PHP extension for libsodium.

Documentation: https://paragonie.com/book/pecl-libsodium

%description -l pl.UTF-8
Proste, niskopoziomowe rozszerzenie PHP do libsodium.

Dokumentacja: https://paragonie.com/book/pecl-libsodium

%prep
%setup -qc
%{__mv} %{modname}-%{version}/* .

%build
# Sanity check, really often broken
extver=$(sed -n '/#define PHP_LIBSODIUM_VERSION/{s/.* "//;s/".*$//;p}' php_libsodium.h)
if test "x${extver}" != "x%{version}"; then
	: Error: Upstream extension version is ${extver}, expecting %{version}.
	exit 1
fi

phpize
%configure
%{__make}

%if %{with tests}
: Minimal load test
%{__php} -n \
	-d extension_dir=modules \
	-d extension=%{modname}.so \
	-m > modules.log
grep %{modname} modules.log

: Upstream test suite
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
%{__make} test \
	PHP_EXECUTABLE=%{__php} \
	PHP_TEST_SHARED_SYSTEM_EXTENSIONS="json" \
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	EXTENSION_DIR=%{php_extensiondir} \
	INSTALL_ROOT=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d
cat <<'EOF' > $RPM_BUILD_ROOT%{php_sysconfdir}/conf.d/%{modname}.ini
; Enable %{modname} extension module
extension=%{modname}.so
EOF

%clean
rm -rf $RPM_BUILD_ROOT

%post
%php_webserver_restart

%postun
if [ "$1" = 0 ]; then
	%php_webserver_restart
fi

%files
%defattr(644,root,root,755)
%doc README.md LICENSE
%config(noreplace) %verify(not md5 mtime size) %{php_sysconfdir}/conf.d/%{modname}.ini
%attr(755,root,root) %{php_extensiondir}/%{modname}.so
