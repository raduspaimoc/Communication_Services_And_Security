#!/bin/bash

time=$( tshark -Y "ip.dsfield.dscp == 56  and ip.src ==11.0.0.1" -r captureP1.pcapng -T fields -e frame.time_relative | tail -1)


bytes_array=$(tshark -Y "ip.dsfield.dscp == 56  and ip.src ==11.0.0.1" -r captureP1.pcapng -T fields -e frame.len)
bytes=0
for x in ${bytes_array[*]}; do
	bytes=$[ $bytes + $x ];
done

echo ""
echo "IP Precedence 7"
echo "$bytes bytes"
bits=$[$bytes*8]
average_rate=$(bc <<< "$bits/$time")
echo "Average rate: $average_rate bps"
echo ""

total_bytes=$bytes

bytes_array=$(tshark -Y "ip.dsfield.dscp == 8  and ip.src ==11.0.0.1" -r captureP1.pcapng -T fields -e frame.len)
bytes=0
for x in ${bytes_array[*]}; do
	bytes=$[ $bytes + $x ];
done

echo ""
echo "IP Precedence 1"
echo "$bytes bytes"
bits=$[$bytes*8]
average_rate=$(bc <<< "$bits/$time")
echo "Average rate: $average_rate bps"
echo ""

total_bytes=$[$bytes + $total_bytes]

bytes_array=$(tshark -Y "ip.src ==12.0.0.1" -r captureP1.pcapng -T fields -e frame.len)
bytes=0
for x in ${bytes_array[*]}; do
	bytes=$[ $bytes + $x ];
done

echo ""
echo "IP Without Precedence"
echo "$bytes bytes"
bits=$[$bytes*8]
average_rate=$(bc <<< "$bits/$time")
echo "Average rate: $average_rate bps"
echo ""

total_bytes=$[$bytes + $total_bytes]

echo ""
echo "Total bytes: $total_bytes"
echo ""
