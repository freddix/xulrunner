Summary:	Mozilla Runtime Environment for XUL+XPCOM applications
Name:		xulrunner
Version:	16.0.1
Release:	1
Epoch:		1
License:	MPL v1.1 or GPL v2+ or LGPL v2.1+
Group:		X11/Applications
Source0:	http://releases.mozilla.org/pub/mozilla.org/firefox/releases/%{version}/source/firefox-%{version}.source.tar.bz2
# Source0-md5:	78e641c67dc4a40cb3f48fce3e782d41
Patch0:		%{name}-install-dir.patch
Patch1:		%{name}-pc.patch
Patch2:		%{name}-hunspell.patch
Patch3:		%{name}-system-cairo.patch
Patch4:		%{name}-virtualenv.patch
URL:		http://developer.mozilla.org/en/docs/XULRunner
BuildRequires:	OpenGL-devel
BuildRequires:	automake
BuildRequires:	bzip2-devel
BuildRequires:	cairo-devel >= 1.10.2-2
BuildRequires:	gtk+-devel
BuildRequires:	hunspell-devel
BuildRequires:	libIDL-devel
BuildRequires:	libevent-devel
BuildRequires:	libffi-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libnotify-devel
BuildRequires:	libpng-devel
BuildRequires:	libstdc++-devel
BuildRequires:	libvpx-devel
BuildRequires:	nspr-devel >= 1:4.9
BuildRequires:	nss-devel >= 1:3.13.3
BuildRequires:	pango-devel
BuildRequires:	perl-modules
BuildRequires:	pkg-config
BuildRequires:	python-devel-src
BuildRequires:	sed
BuildRequires:	sqlite3-devel >= 3.7.10
BuildRequires:	startup-notification-devel
BuildRequires:	xorg-libXcursor-devel
BuildRequires:	xorg-libXft-devel
BuildRequires:	zip
BuildRequires:	zlib-devel
BuildConflicts:	xulrunner-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# bug680547
%define		specflags	-mno-avx

%description
XULRunner is a Mozilla runtime package that can be used to bootstrap
XUL+XPCOM applications that are as rich as Firefox and Thunderbird. It
will provide mechanisms for installing, upgrading, and uninstalling
these applications. XULRunner will also provide libxul, a solution
which allows the embedding of Mozilla technologies in other projects
and products.

%package devel
Summary:	Headers for developing programs that will use XULRunner
Group:		X11/Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}
Requires:	nspr-devel
Requires:	nss-devel

%description devel
XULRunner development package.

%prep
%setup -qc

cd mozilla-release
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p2
%patch4 -p1

# use system headers
rm -f extensions/spellcheck/hunspell/src/*.hxx
echo 'LOCAL_INCLUDES += $(MOZ_HUNSPELL_CFLAGS)' >> extensions/spellcheck/src/Makefile.in

# find ../../dist/sdk -name "*.pyc" | xargs rm
# rm: missing operand
sed -i -e "s|xargs rm|xargs rm -f|g" toolkit/mozapps/installer/packager.mk

%build
cd mozilla-release
cp -f %{_datadir}/automake/config.* build/autoconf

cat << 'EOF' > .mozconfig
. $topsrcdir/xulrunner/config/mozconfig

mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/obj-%{_target_cpu}
#
ac_add_options --host=%{_host}
ac_add_options --build=%{_host}
#
ac_add_options --libdir=%{_libdir}
ac_add_options --prefix=%{_prefix}
#
ac_add_options --disable-crashreporter
ac_add_options --disable-installer
ac_add_options --disable-javaxpcom
ac_add_options --disable-logging
ac_add_options --disable-mochitest
ac_add_options --disable-tests
ac_add_options --disable-updater
#
ac_add_options --enable-safe-browsing
ac_add_options --enable-url-classifier
#
ac_add_options --enable-optimize
#
ac_add_options --disable-gnomeui
ac_add_options --disable-gnomevfs
ac_add_options --enable-gio
ac_add_options --enable-startup-notification
#
ac_add_options --enable-system-cairo
ac_add_options --enable-system-hunspell
ac_add_options --enable-system-lcms
ac_add_options --enable-system-sqlite
ac_add_options --enable-system-ffi
ac_add_options --enable-system-pixman
ac_add_options --with-pthreads
ac_add_options --with-system-bz2
ac_add_options --with-system-jpeg
ac_add_options --with-system-libevent
ac_add_options --with-system-libvpx
ac_add_options --with-system-nspr
ac_add_options --with-system-nss
ac_add_options --with-system-png
ac_add_options --with-system-zlib
#
export BUILD_OFFICIAL=1
export MOZILLA_OFFICIAL=1
export MOZ_UA_BUILDID=20100101
mk_add_options BUILD_OFFICIAL=1
mk_add_options MOZILLA_OFFICIAL=1

EOF

export CFLAGS="%{rpmcflags}"
export CXXFLAGS="%{rpmcflags}"
export LDFLAGS="%{rpmldflags} -Wl,-rpath,%{_libdir}/xulrunner"

%{__make} -f client.mk build		\
	CC="%{__cc}"			\
	CXX="%{__cxx}"			\
	MOZ_MAKE_FLAGS=%{?_smp_mflags}	\
	STRIP="/bin/true"

%install
rm -rf $RPM_BUILD_ROOT
cd mozilla-release

%{__make} -j1 -f client.mk install	\
	DESTDIR=$RPM_BUILD_ROOT		\
	STRIP="/bin/true"

install obj-%{_target_cpu}/dist/bin/xpcshell $RPM_BUILD_ROOT%{_libdir}/%{name}
install obj-%{_target_cpu}/dist/bin/run-mozilla.sh $RPM_BUILD_ROOT%{_libdir}/%{name}
ln -sf %{_libdir}/%{name}/run-mozilla.sh $RPM_BUILD_ROOT%{_libdir}/%{name}-devel/sdk/bin/run-mozilla.sh
ln -sf %{_libdir}/%{name}/xpcshell $RPM_BUILD_ROOT%{_libdir}/%{name}-devel/sdk/bin/xpcshell

ln -sf %{_libdir}/%{name}/libmozalloc.so $RPM_BUILD_ROOT%{_libdir}/%{name}-devel/sdk/lib/libmozalloc.so
ln -sf %{_libdir}/%{name}/libxpcom.so $RPM_BUILD_ROOT%{_libdir}/%{name}-devel/sdk/lib/libxpcom.so
ln -sf %{_libdir}/%{name}/libxul.so $RPM_BUILD_ROOT%{_libdir}/%{name}-devel/sdk/lib/libxul.so

mv $RPM_BUILD_ROOT%{_libdir}/%{name}/xulrunner $RPM_BUILD_ROOT%{_bindir}/xulrunner
ln -s %{_bindir}/xulrunner $RPM_BUILD_ROOT%{_libdir}/%{name}/xulrunner

rm -rf $RPM_BUILD_ROOT%{_libdir}/%{name}/dictionaries
ln -s %{_datadir}/myspell $RPM_BUILD_ROOT%{_libdir}/%{name}/dictionaries

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /usr/sbin/ldconfig
%postun	-p /usr/sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/xulrunner
%attr(755,root,root) %{_libdir}/xulrunner/libmozalloc.so
%attr(755,root,root) %{_libdir}/xulrunner/libxpcom.so
%attr(755,root,root) %{_libdir}/xulrunner/libxul.so
%attr(755,root,root) %{_libdir}/xulrunner/mozilla-xremote-client
%attr(755,root,root) %{_libdir}/xulrunner/plugin-container
%attr(755,root,root) %{_libdir}/xulrunner/run-mozilla.sh
%attr(755,root,root) %{_libdir}/xulrunner/xulrunner

%attr(755,root,root) %{_libdir}/xulrunner/components/libdbusservice.so
%attr(755,root,root) %{_libdir}/xulrunner/components/libmozgnome.so

%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/components
%dir %{_libdir}/%{name}/dictionaries
%dir %{_libdir}/%{name}/plugins

%{_libdir}/%{name}/chrome
%{_libdir}/%{name}/chrome.manifest
%{_libdir}/%{name}/components/binary.manifest
%{_libdir}/%{name}/dependentlibs.list
%{_libdir}/%{name}/omni.ja
%{_libdir}/%{name}/platform.ini

%files devel
%defattr(644,root,root,755)

%dir %{_libdir}/%{name}-devel
%dir %{_libdir}/%{name}-devel/bin
%dir %{_libdir}/%{name}-devel/idl
%dir %{_libdir}/%{name}-devel/include
%dir %{_libdir}/%{name}-devel/lib
%dir %{_libdir}/%{name}-devel/sdk
%dir %{_libdir}/%{name}-devel/sdk/bin
%dir %{_libdir}/%{name}-devel/sdk/lib

%attr(755,root,root) %{_libdir}/%{name}-devel/sdk/bin/*
%attr(755,root,root) %{_libdir}/%{name}-devel/sdk/lib/*.so
%{_libdir}/%{name}-devel/sdk/lib/*.desc
%attr(755,root,root) %{_libdir}/%{name}/xulrunner-stub
%attr(755,root,root) %{_libdir}/xulrunner/xpcshell

%{_datadir}/idl/%{name}
%{_includedir}/%{name}
%{_libdir}/%{name}-devel/sdk/lib/*.a
%{_libdir}/%{name}-devel/xpcom-config.h
%{_pkgconfigdir}/*.pc

