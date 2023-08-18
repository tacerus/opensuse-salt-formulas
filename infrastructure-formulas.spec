#
# spec file for package infrastructure-formulas
#
# Copyright (c) 2023 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


%define fdir %{_datadir}/salt-formulas
%define sdir %{fdir}/states
%define mdir %{fdir}/metadata
Name:           infrastructure-formulas
Version:        0.7
Release:        0
Summary:        Custom Salt states for the openSUSE/SUSE infrastructures
License:        GPL-3.0-or-later
Group:          System/Management
URL:            https://github.com/openSUSE/salt-formulas
Source:         _service
Requires:       gitea-formula
Requires:       grains-formula
Requires:       infrastructure-formula
Requires:       jenkins-formula
Requires:       juniper_junos-formula
Requires:       libvirt-formula
Requires:       lock-formula
Requires:       lunmap-formula
Requires:       multipath-formula
Requires:       orchestra-formula
Requires:       os_update-formula
Requires:       rebootmgr-formula
Requires:       redis-formula
Requires:       redmine-formula
Requires:       suse_ha-formula
Requires:       zypper-formula
BuildArch:      noarch

%description
Custom Salt states used in the openSUSE and SUSE infrastructures.

%package common
Summary:        Files and directories shared by formulas
License:        GPL-3.0-or-later

%description common
Files and directories shared by openSUSE/SUSE infrastructure formuas.

%package -n infrastructure-formula
Summary:        Salt states specific to the openSUSE/SUSE infrastructures
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n infrastructure-formula
Custom Salt states specific to the openSUSE/SUSE infrastructures.

%package -n libvirt-formula
Summary:        Salt states for managing libvirt
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n libvirt-formula
Salt states for managing libvirt servers.

%package -n lunmap-formula
Summary:        Salt states for managing lunmap
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n lunmap-formula
Salt states for managing LUN mappings.

%package -n orchestra-formula
Summary:        Salt orchestration helper states
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n orchestra-formula
Salt helper states for the openSUSE/SUSE infrastructure orchestration states.

%package -n suse_ha-formula
Summary:        Salt states for managing SLE HA clusters
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n suse_ha-formula
Salt states for managing SUSE Linux Enterprise HA clusters.

%package -n grains-formula
Summary:        Salt state for managing grains
License:        Apache-2.0
Requires:       %{name}-common

%description -n grains-formula
Salt state for managing grains.

%package -n os_update-formula
Summary:        Salt states for managing os-update
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n os_update-formula
Salt states for managing os-update.

%package -n rebootmgr-formula
Summary:        Salt states for managing rebootmgr
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n rebootmgr-formula
Salt states for managing rebootmgr.

%package -n zypper-formula
Summary:        Salt states for managing zypper
License:        Apache-2.0
Requires:       %{name}-common

%description -n zypper-formula
Salt states for configuring packages, repositories, and zypper itself.

%package -n lock-formula
Summary:        Salt state module for managing lockfiles
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n lock-formula
Salt state module allowing you to place a lock file prior to other states in order to prevent simultaneous executions.

%package -n juniper_junos-formula
Summary:        Salt states for managing Junos
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n juniper_junos-formula
Salt states for managing Juniper Junos based network devices using pillars.

%package -n gitea-formula
Summary:        Salt states for managing Gitea
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n gitea-formula
Salt states for managing Gitea.

%package -n redis-formula
Summary:        Salt states for managing Redis
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n redis-formula
Salt states for managing Redis.

%package -n multipath-formula
Summary:        Salt states for managing multipath
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n multipath-formula
Salt states for installing multipath-tools and managing multipath/multipathd

%package -n redmine-formula
Summary:        Salt states for managing Redmine
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n redmine-formula
Salt states for managing Redmine.

%package -n jenkins-formula
Summary:        Salt states for managing Jenkins
License:        GPL-3.0-or-later
Requires:       %{name}-common

%description -n jenkins-formula
Salt states for managing Jenkins Controller and Agent servers

%prep
mv %{_sourcedir}/salt-formulas-%{version}/* .

%build

%install
install -dm0755 %{buildroot}%{mdir} %{buildroot}%{sdir} %{buildroot}%{sdir}/_modules %{buildroot}%{sdir}/_states %{buildroot}%{_bindir}

dst_execumodules="%{sdir}/_modules"
dst_statemodules="%{sdir}/_states"
dst_bin='%{_bindir}'

for formula in $(find -mindepth 1 -maxdepth 1 -type d -name '*-formula' -printf '%%P\n')
do
  echo "$formula"
  fname="${formula%%-*}"

  src_metadata="$formula/metadata"
  src_states="$formula/$fname"
  if [ ! -d "$src_states" ]
  then
    src_states="$formula/${fname//_/-}"
  fi
  src_execumodules="$formula/_modules"
  src_statemodules="$formula/_states"
  src_bin="$formula/bin"

  dst_metadata="%{mdir}/$fname"
  dst_states="%{sdir}/$fname"

  if [ -d "$src_metadata" ]
  then
    cp -rv "$src_metadata" "%{buildroot}$dst_metadata"
    echo "$dst_metadata" > "$fname.files"
  fi

  if [ -d "$src_states" ]
  then
    cp -rv "$src_states" "%{buildroot}$dst_states"
    echo "$dst_states" >> "$fname.files"
  else
    echo "Warning: $formula does not ship with any states"
  fi

  for mod in execu state bin
  do
    mode=0644
    case "$mod" in
      'execu' ) src="$src_execumodules"
                dst="$dst_execumodules"
      ;;
      'state' ) src="$src_statemodules"
                dst="$dst_statemodules"
      ;;
      'bin' )
                src="$src_bin"
                dst="$dst_bin"
                mode=0755
      ;;
    esac

    if [ -d "$src" ]
    then
      find "$src" -type f \
        -execdir install -vm "$mode" {} "%{buildroot}$dst" \; \
        -execdir sh -cx 'echo "$1/$(basename $2)" >> "$3"' prog "$dst" {} "../../$fname.files" \;
    fi
  done

  for license in 'COPYING' 'LICENCE' 'LICENSE'
  do
    if [ -f "$formula/$license" ]
    then
      echo "%%license $formula/$license" >> "$fname.files"
      break
    fi
  done

done

%files

%files common
%license COPYING
%doc README.md
%dir %{fdir}
%dir %{mdir}
%dir %{sdir}
%dir %{sdir}/_{modules,states}

%files -n infrastructure-formula -f infrastructure.files

%files -n libvirt-formula -f libvirt.files

%files -n lunmap-formula -f lunmap.files

%files -n orchestra-formula -f orchestra.files

%files -n suse_ha-formula -f suse_ha.files

%files -n grains-formula -f grains.files

%files -n os_update-formula -f os_update.files

%files -n rebootmgr-formula -f rebootmgr.files

%files -n zypper-formula -f zypper.files

%files -n lock-formula -f lock.files

%files -n juniper_junos-formula -f juniper_junos.files

%files -n gitea-formula -f gitea.files

%files -n redis-formula -f redis.files

%files -n multipath-formula -f multipath.files

%files -n redmine-formula -f redmine.files

%files -n jenkins-formula -f jenkins.files

%changelog
