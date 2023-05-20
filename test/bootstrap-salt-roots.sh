# Helper utility for installing the openSUSE Salt formulas in a Scullery test environment.
# ---
# Copyright 2023, Georg Pfuetzenreuter

if [ ! -d /srv/formulas ]
then
  mkdir /srv/formulas
fi
if [ ! -d /srv/pillar/samples ]
then
  mkdir /srv/pillar/samples
fi
for formula in $(find /vagrant -mindepth 1 -maxdepth 1 -type d -name '*-formula' -printf '%P\n')
do
  echo "$formula"
  fname="${formula%%-*}"
  src_states="$formula/$fname"
  src_formula="/vagrant/$src_states"
  src_pillar="/vagrant/$formula/pillar.example"
  src_test_pillar="/vagrant/$formula/test/pillar/default.sls"
  if [ ! -d "$src_formula" ]
  then
    fname="${fname//_/-}"
    src_states="$formula/$fname"
    src_formula="/vagrant/$src_states"
  fi
  if [ ! -h "/srv/formulas/$fname" ]
  then
    ln -s "$src_formula" "/srv/formulas"
  fi
  dst_pillar="/srv/pillar/samples/$fname.sls"
  if [ -f "$src_test_pillar" ]
  then
    cp "$src_test_pillar" "$dst_pillar"
  elif [ -f "$src_pillar" ]
  then
    cp "$src_pillar" "$dst_pillar"
  fi
done
tee /srv/pillar/top.sls >/dev/null <<EOF
{{ saltenv }}:
  '*':
    - full
EOF
tee /srv/pillar/full.sls >/dev/null <<EOF
include:
  - samples.*
EOF

