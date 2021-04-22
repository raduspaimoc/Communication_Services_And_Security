#!/bin/bash
function rate(){
	input_file=$1
	output_file=$2

	times=$( tshark -Y "ip.src ==14.0.0.1" -r "$input_file" -T fields -e frame.time_relative)
	time=(${times// / })

	bytes_arrays=$(tshark -Y "ip.src ==14.0.0.1" -r "$input_file" -T fields -e frame.len)
	bytes_array=(${bytes_arrays// / })

	bytes=0
	echo "Creating CSV"
	echo "time,bytes,rate">"$output_file"
	last_time=0
	tlen=${#time[@]}
	t=0.0
	b=0.0
	r=0.0
	echo "Calculating CSV $tlen"
	for ((i=0; i<$tlen;i++)) do
		t=${time[$i]}
		b=$(bc <<< "${bytes_array[$i]}+$b")

		dif=$(bc <<< "$t-$last_time>=1.0")
		#echo "$t b $b"
		if [ "$dif" -eq "1" ]; then
			#echo "$t $b"
			r=$(bc <<< "($b/($t-$last_time))")
			echo "$t,$b,$r">>"$output_file"
			b=0
			last_time=$t
			#sleep 1
		fi

	done

}

rate "no_shapping.pcapng" "avg_no_shapping.csv"
