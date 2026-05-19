%define rpmroot             /usr/lib/pqrpm
%define rpmhome             %{rpmroot}/lib/rpm
%define rpmdb               %{rpmroot}/lib/sysimage/rpm
%define _bindir             %{rpmroot}/bin
%define _libdir             %{rpmroot}/%{_lib}
%define _datadir            %{rpmroot}/share
%define _includedir         %{rpmroot}/include
%define _sysconfdir         %{rpmroot}/etc
%define _sharedstatedir     %{rpmroot}/var/lib
%define _mandir             %{_datadir}/man
%define _defaultdocdir      %{_datadir}/doc
%define _defaultlicensedir  %{_datadir}/licenses

%global rpmver 4.19.1.1
#global snapver rc1
%global baserelease 6
%global sover 10

%global srcver %{rpmver}%{?snapver:-%{snapver}}
%global srcdir %{?snapver:testing}%{!?snapver:rpm-%(echo %{rpmver} | cut -d'.' -f1-2).x}

Summary: The RPM package management system (PQC edition)
Name: pqrpm
Version: %{rpmver}
Release: %{?snapver:0.%{snapver}.}%{baserelease}%{?dist}
Url: http://www.rpm.org/
License: GPL-2.0-or-later
Source0: http://ftp.rpm.org/releases/%{srcdir}/rpm-%{srcver}.tar.bz2

Source30: macros.rpmsign-sequoia

Requires: coreutils
Requires: popt%{_isa} >= 1.10.2.1
Requires: curl

# XXX generally assumed to be installed but make it explicit as rpm
# is a bit special...
BuildRequires: redhat-rpm-config >= 94
BuildRequires: systemd-rpm-macros
BuildRequires: gcc make
BuildRequires: cmake >= 3.18
BuildRequires: gawk
BuildRequires: readline-devel zlib-devel
# The popt version here just documents an older known-good version
BuildRequires: popt-devel >= 1.10.2
BuildRequires: file-devel
BuildRequires: gettext-devel
BuildRequires: ncurses-devel
BuildRequires: bzip2-devel >= 0.9.0c-2
BuildRequires: lua-devel >= 5.1
BuildRequires: libcap-devel
BuildRequires: libacl-devel
BuildRequires: sqlite-devel
BuildRequires: rpm-sequoia-devel >= 1.9.0

# Couple of patches change makefiles so, require for now...
BuildRequires: automake libtool

%patchlist
# Set rpmdb path to /usr/lib/sysimage/rpm
rpm-4.17.x-rpm_dbpath.patch
# Disable autoconf config.site processing (#962837)
rpm-4.18.x-siteconfig.patch
# In current Fedora, man-pages pkg owns all the localized man directories
rpm-4.9.90-no-man-dirs.patch
# Disable new user/group handling

rpm-4.18.92-disable-sysusers.patch
rpm-4.18.90-weak-user-group.patch

# Patches already upstream:
0001-Fix-potential-use-of-uninitialized-pipe-array.patch
0001-Fix-potential-use-of-uninitialized-pgp-struct.patch
0001-Fix-memory-leak-in-rpmsign.patch

0001-Refactor-sign-command-expand-and-parse-out-of-runGPG.patch
0002-Eliminate-hardcoded-GPG-references-from-user-visible.patch
0003-Declare-signCmd-static.patch

0001-Report-unsafe-symlinks-during-installation-as-a-spec.patch
0002-Fix-FA_TOUCH-ed-files-getting-removed-on-failed-upda.patch

0001-Fix-possible-package-corruption-on-delsign-resign-ad.patch
0002-Fix-regression-on-build-id-generation-from-compresse.patch
0003-Fix-root-relocation-regression.patch

0001-Make-_passwd_path-and-_group_path-lists.patch
0002-Fix-memory-leak-in-rpmspec-shell.patch
0003-Fix-memory-leak-in-runGPG.patch
0004-Talk-about-rpmsign-in-the-rpmsign-man-page.patch
0005-Revert-Drop-redundant-argument-from-rpmcliTransactio.patch
0001-Store-configurable-digest-s-on-packages-from-verific.patch
0001-Ensure-binary-and-source-headers-are-identified-as-s.patch
0002-Add-support-for-spec-local-file-attributes-and-gener.patch

rpm-4.19.x-rpmkeys-add-list-erase.patch

# PQC readiness
0001-Extend-RPM-version-output-with-PQC-edition.patch
rpm-4.19.x-multisig.patch
rpm-4.19.x-pqc-algo.patch
rpm-4.19.x-pqc-fixes.patch

rpm-4.19.x-multisig-verify-fixes.patch

# These are not yet upstream
rpm-4.7.1-geode-i686.patch

%description
A minimal edition of The RPM Package Manager (RPM) with support for adding and
verifying Post-Quantum Cryptography (PQC) package signatures. This edition is
not intended for general use such as installing or removing packages, and is
installed into its own prefix at %{rpmroot} to avoid clashing with the system
RPM.

%package libs
Summary:  Libraries for manipulating RPM packages
License:  GPL-2.0-or-later OR LGPL-2.1-or-later
Requires(meta): %{name} = %{version}-%{release}
# >= 1.4.0 required for pgpVerifySignature2() and pgpPrtParams2()
Requires: rpm-sequoia%{_isa} >= 1.9.0

%description libs
This package contains the RPM shared libraries.

%package sign-libs
Summary:  Libraries for signing RPM packages
Requires: %{name}-libs%{_isa} = %{version}-%{release}
Requires: gnupg2

%description sign-libs
This package contains the RPM shared libraries for signing packages.

%package sign
Summary: Package signing support
Requires: %{name}-sign-libs%{_isa} = %{version}-%{release}

%description sign
This package contains support for digitally signing RPM packages.

%prep
%autosetup -n rpm-%{srcver} -p1

%build
%set_build_flags

mkdir _build
cd _build
cmake \
      -DCMAKE_INSTALL_PREFIX=%{rpmroot} \
      -DCMAKE_INSTALL_RPATH=%{_libdir} \
      -DCMAKE_INSTALL_SHAREDSTATEDIR:PATH=%{_sharedstatedir} \
      -DENABLE_PYTHON=OFF \
      -DENABLE_NDB=OFF \
      -DENABLE_PLUGINS=OFF \
      -DENABLE_TESTSUITE=OFF \
      -DWITH_SEQUOIA=ON \
      -DWITH_ARCHIVE=OFF \
      -DWITH_AUDIT=OFF \
      -DWITH_DBUS=OFF \
      -DWITH_FAPOLICYD=OFF \
      -DWITH_SELINUX=OFF \
      -DRPM_VENDOR=redhat \
  ..

%make_build

%install
cd _build
%make_install

mkdir -p $RPM_BUILD_ROOT%{rpmhome}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rpm
mkdir -p $RPM_BUILD_ROOT%{rpmhome}/macros.d
mkdir -p $RPM_BUILD_ROOT%{rpmdb}
mkdir -p $RPM_BUILD_ROOT%{_defaultlicensedir}

# init an empty database for %ghost'ing for all supported backends
mkdir sqlite
RPM_CONFIGDIR=$PWD tools/rpmdb --define "_db_backend sqlite" --dbpath=${PWD}/sqlite --initdb
cp -va sqlite/. $RPM_BUILD_ROOT%{rpmdb}/

find $RPM_BUILD_ROOT -name "*.la"|xargs rm -f

rm $RPM_BUILD_ROOT/%{_bindir}/rpm
rm $RPM_BUILD_ROOT/%{_bindir}/rpm2cpio
rm $RPM_BUILD_ROOT/%{_bindir}/rpmquery
rm $RPM_BUILD_ROOT/%{_bindir}/rpmverify
rm $RPM_BUILD_ROOT/%{_bindir}/rpmsort
rm $RPM_BUILD_ROOT/%{_bindir}/rpmbuild
rm $RPM_BUILD_ROOT/%{_bindir}/gendiff
rm $RPM_BUILD_ROOT/%{_bindir}/rpmspec
rm $RPM_BUILD_ROOT/%{_bindir}/rpmlua
rm $RPM_BUILD_ROOT/%{_bindir}/rpmgraph

rm $RPM_BUILD_ROOT/%{_mandir}/man8/rpm.8*
rm $RPM_BUILD_ROOT/%{_mandir}/man8/rpm2cpio.8*
rm $RPM_BUILD_ROOT/%{_mandir}/man8/rpm-misc.8*
rm $RPM_BUILD_ROOT/%{_mandir}/man8/rpmsort.8*
rm $RPM_BUILD_ROOT/%{_mandir}/man1/gendiff.1*
rm $RPM_BUILD_ROOT/%{_mandir}/man8/rpmbuild.8*
rm $RPM_BUILD_ROOT/%{_mandir}/man8/rpmdeps.8*
rm $RPM_BUILD_ROOT/%{_mandir}/man8/rpmspec.8*
rm $RPM_BUILD_ROOT/%{_mandir}/man8/rpmlua.8*
rm $RPM_BUILD_ROOT/%{_mandir}/man8/rpmgraph.8*

rm -rf $RPM_BUILD_ROOT/var/tmp
find $RPM_BUILD_ROOT/%{_defaultdocdir} ! -name COPYING -type f -exec rm -f {} +
rm -rf $RPM_BUILD_ROOT/%{_datadir}/locale
rm -rf $RPM_BUILD_ROOT/%{_fileattrsdir}
rm -rf $RPM_BUILD_ROOT/%{_includedir}
rm -rf $RPM_BUILD_ROOT/%{_libdir}/cmake/rpm

rm $RPM_BUILD_ROOT/%{rpmhome}/rpm.daily
rm $RPM_BUILD_ROOT/%{rpmhome}/rpm2cpio.sh
rm $RPM_BUILD_ROOT/%{rpmhome}/tgpg
rm $RPM_BUILD_ROOT/%{rpmhome}/sysusers.sh
rm $RPM_BUILD_ROOT/%{rpmhome}/brp-*
rm $RPM_BUILD_ROOT/%{rpmhome}/check-*
rm $RPM_BUILD_ROOT/%{rpmhome}/find-lang.sh
rm $RPM_BUILD_ROOT/%{rpmhome}/*provides*
rm $RPM_BUILD_ROOT/%{rpmhome}/*requires*
rm $RPM_BUILD_ROOT/%{rpmhome}/*deps*
rm $RPM_BUILD_ROOT/%{rpmhome}/*.prov
rm $RPM_BUILD_ROOT/%{rpmhome}/*.req
rm $RPM_BUILD_ROOT/%{rpmhome}/fileattrs/*
rm $RPM_BUILD_ROOT/%{rpmhome}/rpmuncompress
rm $RPM_BUILD_ROOT/%{rpmhome}/rpm.log
rm $RPM_BUILD_ROOT/%{rpmhome}/rpm.supp
rm $RPM_BUILD_ROOT/%{rpmhome}/rpmdb_dump
rm $RPM_BUILD_ROOT/%{rpmhome}/rpmdb_load
rm $RPM_BUILD_ROOT/%{rpmhome}/rpmdump

rm $RPM_BUILD_ROOT/%{_libdir}/librpmbuild.so.*
rm $RPM_BUILD_ROOT/%{_libdir}/librp*[a-z].so
rm $RPM_BUILD_ROOT/%{_libdir}/pkgconfig/rpm.pc

# Signing macros for Sequoia
install -m 644 %{SOURCE30} $RPM_BUILD_ROOT/%{_defaultdocdir}/rpm/

%files
%license COPYING
%doc %{_defaultdocdir}/rpm/COPYING
%dir %{rpmroot}
%dir %{rpmroot}/lib
%dir %{rpmroot}/lib/sysimage
%dir %{_bindir}
%dir %{_datadir}
%dir %{_mandir}
%dir %{_mandir}/*
%dir %{_sysconfdir}
%dir %{_sysconfdir}/rpm
%dir %{_defaultdocdir}
%dir %{_defaultdocdir}/rpm
%dir %{_defaultlicensedir}
%{_bindir}/rpmdb
%{_bindir}/rpmkeys
%{_mandir}/man8/rpmdb.8*
%{_mandir}/man8/rpmkeys.8*
%attr(0755, root, root) %dir %{rpmdb}
%attr(0644, root, root) %ghost %config(missingok,noreplace) %{rpmdb}/*
%attr(0644, root, root) %ghost %{rpmdb}/.*.lock
%attr(0755, root, root) %dir %{rpmhome}
%{rpmhome}/macros
%dir %{rpmhome}/macros.d
%{rpmhome}/rpmpopt*
%{rpmhome}/rpmrc
%{rpmhome}/platform

%files libs
%dir %{_libdir}
%{_libdir}/librpmio.so.%{sover}
%{_libdir}/librpm.so.%{sover}
%{_libdir}/librpmio.so.%{sover}.*
%{_libdir}/librpm.so.%{sover}.*

%files sign-libs
%{_libdir}/librpmsign.so.%{sover}
%{_libdir}/librpmsign.so.%{sover}.*

%files sign
%{_bindir}/rpmsign
%{_mandir}/man8/rpmsign.8*
%doc %{_defaultdocdir}/rpm/macros.rpmsign-sequoia

%changelog
* Thu Feb 05 2026 Michal Domonkos <mdomonko@redhat.com> - 4.19.1.1-6
- Fix key import API to return NOTTRUSTED for disabled algorithms (RHEL-112700)

* Mon Feb 02 2026 Michal Domonkos <mdomonko@redhat.com> - 4.19.1.1-5
- Ignore signatures made by unknown or disabled algorithms (RHEL-112700)

* Tue Aug 26 2025 Michal Domonkos <mdomonko@redhat.com> - 4.19.1.1-4
- Fix rpmsign(8) man page (RHEL-109233)

* Mon Aug 25 2025 Michal Domonkos <mdomonko@redhat.com> - 4.19.1.1-3
- Additional PQC-related fixes (RHEL-109233)

* Thu Aug 14 2025 Michal Domonkos <mdomonko@redhat.com> - 4.19.1.1-2
- Add signing support (RHEL-107536)

* Mon Aug 04 2025 Michal Domonkos <mdomonko@redhat.com> - 4.19.1.1-1
- Initial commit on c9s (RHEL-84699)
