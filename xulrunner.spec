Summary:	Mozilla Runtime Environment for XUL+XPCOM applications
Name:		xulrunner
Version:	25.0.1
Release:	1
Epoch:		1
License:	MPL v1.1 or GPL v2+ or LGPL v2.1+
Group:		X11/Applications
Source0:	ftp://ftp.mozilla.org/pub/firefox/releases/%{version}/source/firefox-%{version}.source.tar.bz2
# Source0-md5:	b5b57d3ea937a339e0ed7ebea604b430
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
BuildRequires:	gstreamer010-plugins-base-devel
BuildRequires:	gtk+-devel
BuildRequires:	hunspell-devel
BuildRequires:	libIDL-devel
BuildRequires:	libevent-devel
BuildRequires:	libffi-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libnotify-devel
BuildRequires:	libpng-devel >= 2:1.5.13
BuildRequires:	libstdc++-devel
BuildRequires:	libvpx-devel
BuildRequires:	nspr-devel >= 1:4.10.2
BuildRequires:	nss-devel >= 1:3.15.3
BuildRequires:	pango-devel
BuildRequires:	perl-modules
BuildRequires:	pkg-config
BuildRequires:	python-devel-src
BuildRequires:	sed
BuildRequires:	sqlite3-devel >= 3.7.15.2
BuildRequires:	startup-notification-devel
BuildRequires:	xorg-libXcursor-devel
BuildRequires:	xorg-libXft-devel
BuildRequires:	zip
BuildRequires:	zlib-devel
BuildConflicts:	xulrunner
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
#%%patch3 -p2
%patch4 -p1

# use system headers
%{__rm} extensions/spellcheck/hunspell/src/*.hxx
echo 'LOCAL_INCLUDES += $(MOZ_HUNSPELL_CFLAGS)' >> extensions/spellcheck/src/Makefile.in

# find ../../dist/sdk -name "*.pyc" | xargs rm
# rm: missing operand
%{__sed} -i "s|xargs rm|xargs rm -f|g" toolkit/mozapps/installer/packager.mk

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
ac_add_options --enable-optimize="-O2"
#
ac_add_options --disable-gnomeui
ac_add_options --disable-gnomevfs
ac_add_options --enable-gio
ac_add_options --enable-gstreamer
ac_add_options --enable-startup-notification
#
#ac_add_options --enable-system-cairo
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

# generate smaller debug files
export CFLAGS="%(echo %{rpmcflags} | sed 's/ -g2/ -g1/g')"
export CXXFLAGS="%(echo %{rpmcxxflags} | sed 's/ -g2/ -g1/g')"
export LDFLAGS="%{rpmldflags} -Wl,-rpath,%{_libdir}/xulrunner"

# i686 build broken:
#
# Traceback (most recent call last):
# File "./config.status", line 947, in <module>
# config_status(**args)
# File "/home/users/builder/rpm/BUILD/xulrunner-23.0/mozilla-release/build/ConfigStatus.py", line 117, in config_status
# log_manager.add_terminal_logging(level=log_level)
# File "/home/users/builder/rpm/BUILD/xulrunner-23.0/mozilla-release/python/mach/mach/logging.py", line 181, in add_terminal_logging
# if self.terminal:
# File "/home/users/builder/rpm/BUILD/xulrunner-23.0/mozilla-release/python/mach/mach/logging.py", line 153, in terminal
# terminal = blessings.Terminal(stream=sys.stdout)
# File "/home/users/builder/rpm/BUILD/xulrunner-23.0/mozilla-release/python/blessings/blessings/__init__.py", line 98, in __init__
# self._init_descriptor)
# _curses.error: setupterm: could not find terminal
#
# workaround:
export TERM=xterm

%{__make} -f client.mk configure
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
%attr(755,root,root) %{_libdir}/xulrunner/libxul.so
%attr(755,root,root) %{_libdir}/xulrunner/mozilla-xremote-client
%attr(755,root,root) %{_libdir}/xulrunner/plugin-container
%attr(755,root,root) %{_libdir}/xulrunner/run-mozilla.sh
%attr(755,root,root) %{_libdir}/xulrunner/xulrunner

%attr(755,root,root) %{_libdir}/xulrunner/components/libdbusservice.so
%attr(755,root,root) %{_libdir}/xulrunner/components/libmozgnome.so

%dir %{_libdir}/xulrunner
%dir %{_libdir}/xulrunner/components
%dir %{_libdir}/xulrunner/dictionaries

%{_libdir}/xulrunner/chrome
%{_libdir}/xulrunner/chrome.manifest
%{_libdir}/xulrunner/components/components.manifest
%{_libdir}/xulrunner/dependentlibs.list
%{_libdir}/xulrunner/omni.ja
%{_libdir}/xulrunner/platform.ini

%files devel
%defattr(644,root,root,755)

%dir %{_libdir}/xulrunner-devel
%dir %{_libdir}/xulrunner-devel/bin
%dir %{_libdir}/xulrunner-devel/idl
%dir %{_libdir}/xulrunner-devel/include
%dir %{_libdir}/xulrunner-devel/lib
%dir %{_libdir}/xulrunner-devel/sdk
%dir %{_libdir}/xulrunner-devel/sdk/bin
%dir %{_libdir}/xulrunner-devel/sdk/lib

%attr(755,root,root) %{_libdir}/xulrunner-devel/sdk/bin/*
%attr(755,root,root) %{_libdir}/xulrunner-devel/sdk/lib/*.so
%{_libdir}/xulrunner-devel/sdk/lib/*.desc
%attr(755,root,root) %{_libdir}/xulrunner/xulrunner-stub
%attr(755,root,root) %{_libdir}/xulrunner/xpcshell

%{_datadir}/idl/xulrunner
%{_includedir}/xulrunner
%{_libdir}/xulrunner-devel/sdk/lib/*.a
%{_libdir}/xulrunner-devel/xpcom-config.h
%{_pkgconfigdir}/*.pc

