while true;
do
  sudo ./packETHcli -i tap0 -d 8336 -m 2 -f ’ping-1000-tap0.pcap’ -t 1;
   sleep 1;
done