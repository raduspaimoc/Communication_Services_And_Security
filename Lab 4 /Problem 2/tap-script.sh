#!/bin/bash
sudo tunctl -t tap0 -u radu
sudo tunctl -t tap1 -u radu
sudo ip link set tap0 up
sudo ip link set tap1 up
ip add add 11.0.0.1/24 dev tap0
ip add add 12.0.0.1/24 dev tap1
route add -net 13.0.0.0/24 gw 11.0.0.2 dev tap0
route add -net 14.0.0.0/24 gw 12.0.0.2 dev tap1

