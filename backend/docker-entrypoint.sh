#!/bin/sh

set -e

if [ "$(find /tmp/.ssh -maxdepth 1 -regextype posix-extended -regex '.+/id_\w+(.pub)?' -print | wc -l)" -ge "2" ]; then
  cp -R /tmp/.ssh /root/.ssh
  chmod 700 /root/.ssh
  chmod 644 /root/.ssh/*
  find /root/.ssh -maxdepth 1 -regextype posix-extended -regex '.+/id_\w+' -exec chmod 600 '{}' \;
fi

if [ -z "$(ls -A /akvo-flow-server-config)" ] && [ -n "$(find /root/.ssh -maxdepth 1 -name 'id_*.pub' -print -quit)" ]; then
  git clone git@github.com:akvo/akvo-flow-server-config.git /akvo-flow-server-config
fi

exec "$@"
