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
	echo "Total bytes: $bytes bytes."

	bits=$[$bytes*8]
	average_rate=$(bc <<< "$bits/$time")
	echo ""
	echo "Average rate: $average_rate bps."
	echo "-------------------------------"
	echo ""
}

# Gets trace duration
time=$( tshark -Y "ip.dsfield.dscp == 56  and ip.src ==11.0.0.1" -r Capture.pcapng -T fields -e frame.time_relative | tail -1)
echo "Trace duration: $time s."

# Gets bytes array with IP Precedence 7
bytes_array=$(tshark -Y "ip.dsfield.dscp == 56  and ip.src ==11.0.0.1" -r Capture.pcapng -T fields -e frame.len)

# Computes total bytes and avg rate with IP Precedence 7
echo "--------IP Precedence 7--------"
get_total_bytes "${bytes_array[@]}"
total_bytes=$bytes

# Repeats the same process
bytes_array=$(tshark -Y "ip.dsfield.dscp == 8  and ip.src ==11.0.0.1" -r Capture.pcapng -T fields -e frame.len)
echo "--------IP Precedence 1--------"
get_total_bytes "${bytes_array[@]}"
total_bytes=$[$bytes + $total_bytes]

# Repeats the same process
bytes_array=$(tshark -Y "ip.src ==12.0.0.1" -r Capture.pcapng -T fields -e frame.len)
echo "----IP Without Precendence-----"
get_total_bytes "${bytes_array[@]}"
total_bytes=$[$bytes + $total_bytes]

echo "Total bytes: $total_bytes"
