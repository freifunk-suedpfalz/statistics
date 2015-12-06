#!/bin/bash

set -e

#config pfad influxdb
# ToDo check if curl and apt-transport-https exists

if [ "$(whoami)" != "root" ]; then
  echo "Sorry, you are not root."
  exit 1
fi

apt-get upgrade
apt-get dist-upgrade

INFLUXDBCONF=/etc/influxdb/influxdb.generated.conf
PACKAGES="curl wget apt-transport-https jq python3 python3-pip"

apt-get update

for pkg in $PACKAGES ; do
  #if [ "dpkg -l | awk {'print $2'} | grep --regexp=^$pkg$ != """ ]; then
    #echo "$pkg is installed"
  #else
    if apt-get -qq install $pkg; then
      echo "Successfully installed $pkg"
    else
      echo "Error installing $pkg"
      exit 1
    fi
  #fi
done

# Install Grafana through APT
# Use the below line even if you are on Ubuntu or another Debian version.

echo "deb https://packagecloud.io/grafana/stable/debian/ wheezy main" >> /etc/apt/sources.list
curl https://packagecloud.io/gpg.key | apt-key add -

apt-get update
apt-get install grafana


## Install of Grafana through dpkg
cd /tmp
wget http://influxdb.s3.amazonaws.com/influxdb_0.9.5.1_amd64.deb
dpkg -i influxdb_0.9.5.1_amd64.deb

cp /etc/influxdb/influxdb.conf /etc/influxdb/influxdb.generated.conf

#replace configuration file in influxdb.service
sed -i 's/influxdb.conf/influxdb.generated.conf/g' /etc/systemd/system/multi-user.target.wants/influxdb.service

#folder for json formating/parsing
mkdir /usr/local/bin/json_parsing

#install influxdb client for python3
pip3 install influxdb

systemctl daemon-reload

#start influxdb on boot
systemctl enable influxd.service

#start grafana on boot
systemctl enable grafana-server.service

