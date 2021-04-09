#!/bin/bash

# Authors
# Radu Spaimoc & Lluís Mas
echo "Analyzing...."

# Computes total bytes from bytes array
get_total_bytes(){
	bytes_array=("$@")
	bytes=0
	for x in $bytes_array; do
		bytes=$[ $bytes + $x ];
	done
}

bytes1=0
bytes2=0


bytes_array=$(tshark -Y "ip.src ==11.0.0.1" -r captureP2.pcapng -T fields -e frame.len)
get_total_bytes "${bytes_array[@]}"
bytes1=$bytes
total_bytes=$bytes

bytes_array=$(tshark -Y "ip.src ==12.0.0.1" -r captureP2.pcapng -T fields -e frame.len)
get_total_bytes "${bytes_array[@]}"
bytes2=$bytes

total_bytes=$[$bytes + $total_bytes]
bo_1=$(bc <<< "($bytes1*100.0)/$total_bytes")
bo_2=$(bc <<< "($bytes2*100.0)/$total_bytes")

echo "-------------------------------"
echo "Total bytes transfered: $total_bytes Bytes"
echo "-------------------------------"
echo "TAP 0: $bytes1 Bytes"
echo "Bandwidth occupation TAP 0: $bo_1%"
echo "-------------------------------"
echo "TAP 1: $bytes2 Bytes"
echo "Bandwidth occupation TAP 1: $bo_2%"
echo "-------------------------------"

