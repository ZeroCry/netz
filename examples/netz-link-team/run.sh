#!/usr/bin/env bash

sleep 2s

local=$1
remote=$2
mode=$3

teamd -d
ip link set eth0 down
ip link set eth1 down
teamdctl -v team0 port add eth0
teamdctl -v team0 port add eth1

ip link set team0 up
ip address add $local dev team0
ip route add $remote dev team0

if [ "$mode" == "server" ]; then
  iperf -f K -s
else
  echo Starting client in 2s
  sleep 2s
  iperf -f K -c $remote
fi
