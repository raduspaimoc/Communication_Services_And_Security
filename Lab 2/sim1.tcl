# TCP Original (RFC 793)
if {$argc == 2} {
    set karn   [lindex $argv 0] 
    set jacobson       [lindex $argv 1] 
} else {
    puts "      CBR0-UDP n0"
    puts "                \\"
    puts "                 n2 ---- n3"
    puts "                /"
    puts "      CBR1-TCP n1 "
    puts ""
    puts "  Usage: ns $argv0 karn (true|false) jacobson (true|false)"
    puts ""
    exit 1
}

# Createing the simulator object
set ns [new Simulator]

#file to store results
#
if {$karn==false} {
   set arxiu "sor1"
} elseif {$jacobson==false} {
   set arxiu "sor2" 
  } else {
   set arxiu "sor3" 
  }

set nf [open $arxiu.tr w]
$ns trace-all $nf
set nff [open $arxiu.rtt w]

#Finishing procedure
proc finish {} {
        global ns nf nff
        $ns flush-trace
        close $nf
        close $nff
        exit 0
}

# TCP times recording procedure
proc record { } {
	global ns tcp0 nff
    set rtt  [expr [$tcp0 set rtt_]  * [$tcp0 set tcpTick_]]
    set srtt  [expr ([$tcp0 set srtt_] >> [$tcp0 set T_SRTT_BITS]) * [$tcp0 set tcpTick_]]
    set rttvar  [expr ([$tcp0 set rttvar_] >> [$tcp0 set T_RTTVAR_BITS]) * [$tcp0 set tcpTick_]]
    set bo [expr [$tcp0 set backoff_]]  
#  bo = 1, 2, 4, ...
    set rto [expr [$tcp0 set rto_] * [$tcp0 set tcpTick_]]
	set now [$ns now]
	puts $nff "$now $rtt $srtt $rto [expr 0.5*($bo-1)]"

	$ns at [expr $now+0.1] "record"
}

#Create 4 nodes
#
#  n0
#  \
#   \
#    n2--------n3
#   /
#  /
# n1
 
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]

#Duplex lines between nodes
$ns duplex-link $n0 $n2 5Mb 20ms DropTail
$ns duplex-link $n1 $n2 5Mb 20ms DropTail
$ns duplex-link $n2 $n3 1Mb 50ms DropTail


# Node 0:  UDP agent with CBR traffic generator
set udp0 [new Agent/UDP]
$ns attach-agent $n0 $udp0
set cbr0 [new Application/Traffic/CBR]
$cbr0 set rate_ 0.5Mbps
$cbr0 attach-agent $udp0
$udp0 set class_ 0  # Flow identifier


# Node 1: TCP agent using  Karn/Partridge with CBR traffic generator
set tcp0 [new Agent/TCP/RFC793edu]
$tcp0 set class_ 1  # Flow identifier
$tcp0 set add793karnrtt_ $karn
$tcp0 set add793jacobsonrtt_ $jacobson
$tcp0 set add793expbackoff_ false
$tcp0 set add793slowstart_ false
$ns attach-agent $n1 $tcp0
$tcp0 set tcpTick_ 0.01

set cbr1 [new Application/Traffic/CBR]
$cbr1 set rate_ 0.5Mbps
$cbr1 attach-agent $tcp0

# Node 3:  2 Sinks
set null0 [new Agent/Null]
$ns attach-agent $n3 $null0
set null1 [new Agent/TCPSink]
$ns attach-agent $n3 $null1

# Connect agents
$ns connect $udp0 $null0  
$ns connect $tcp0 $null1

# Start CBR0 source at time 5 seconds. Stopping at time 10 s.

$ns at 5.0 "$cbr0 start"
$ns at 10.0 "$cbr0 stop"

$ns at 0.0 "$cbr1 start"
$ns at 0.0 "record"
$ns at 15.0 "finish"

$tcp0 attach-trace $nff

#Running simulation
$ns run
