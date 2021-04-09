#!/bin/bash

bytes_array=$(tshark -Y "ip.src ==11.0.0.1" -r captureP2.pcapng -T fields -e frame.len)
bytes1=0
for x in ${bytes_array[*]}; do
	bytes1=$[ $bytes1 + $x ];
done



total_bytes=$bytes1

bytes_array=$(tshark -Y "ip.src ==12.0.0.1" -r captureP2.pcapng -T fields -e frame.len)
bytes=0
for x in ${bytes_array[*]}; do
	bytes=$[ $bytes + $x ];
done

total_bytes=$[$bytes + $total_bytes]

echo ""
echo "Total bytes transfered: $total_bytes Bytes"
bandwith_occupation1=$(bc <<< "($bytes1*100.0)/$total_bytes")
echo ""
echo "TAP 0: $bytes1 Bytes"
echo "Bandwidth occupation TAP 0: $bandwith_occupation1%"
echo ""
bandwith_occupation=$(bc <<< "($bytes*100.0)/$total_bytes")
echo "TAP 1: $bytes Bytes"
echo "Bandwidth occupation TAP 1: $bandwith_occupation%"
echo ""

