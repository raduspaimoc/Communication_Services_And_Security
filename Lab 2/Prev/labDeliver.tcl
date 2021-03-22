# Creating topology

puts "      CBR2-TCP2     n2"
puts "      Vegas          \\"
puts "                      \\"
puts "     CBR1-TCP1 n1 ---- n3 -----n4"
puts "     Reno             /"
puts "                     /"
puts "     CBR0-TCP0    n0 "
puts "     Tahoe"

puts ""

# Createing the simulator object
set ns [new Simulator]

#file to store results
#
set fname "ex2-trace" 
set nf [open $fname.tr w]
$ns trace-all $nf
set nff [open $fname.rtt w]

#Finishing procedure
proc finish {} {
        global ns nf nff
        $ns flush-trace
        close $nf
        close $nff
        exit 0
}

# Procedure to record TCP times
proc recordTCPTimes { } {
	
	global ns tcp_agents nff cbr_i
	
	set now [$ns now]
	
    for { set index 0 }  { $index < [array size tcp_agents] }  { incr index } {
        writeAgent $tcp_agents($index) $index $nff $now
    }

	$ns at [expr $now+0.1] "recordTCPTimes"
}

# Logging multiple values
proc writeAgent { tcp n nff now args } {
    set rtt  [expr [$tcp set rtt_]  * [$tcp set tcpTick_]]
    set srtt  [expr ([$tcp set srtt_] >> [$tcp set T_SRTT_BITS]) * [$tcp set tcpTick_]]
    set rttvar  [expr ([$tcp set rttvar_] >> [$tcp set T_RTTVAR_BITS]) * [$tcp set tcpTick_]]
    set bo [expr [$tcp set backoff_]]
    set cwnd  [expr [$tcp set cwnd_]]
    set cwmax  [expr [$tcp set cwmax_]]
    puts $nff "$n $now $rtt $srtt $cwnd $cwmax [expr 0.5*($bo-1)]"
}

#Create 5 nodes
#
#  	     n2
#  	      |
#   	      |
#    n1-------n3--------n4
#   	      |
#  	      |
# 	      n0
 
set n(0) [$ns node]
set n(1) [$ns node]
set n(2) [$ns node]
set n(3) [$ns node]
set n(4) [$ns node]

set tcp_agents(0) [new Agent/TCP]
set tcp_agents(1) [new Agent/TCP/Reno]
set tcp_agents(2) [new Agent/TCP/Vegas]

set cbr_i(0) [new Application/Traffic/CBR]
set cbr_i(1) [new Application/Traffic/CBR]
set cbr_i(2) [new Application/Traffic/CBR]

#Duplex lines between nodes
$ns duplex-link $n(0) $n(3) 5Mb 20ms DropTail
$ns duplex-link $n(1) $n(3) 5Mb 20ms DropTail
$ns duplex-link $n(2) $n(3) 5Mb 20ms DropTail
$ns duplex-link $n(3) $n(4) 1Mb 50ms DropTail

# Node 0: CBR0 TCP0 Tahoe
for { set index 0 }  { $index < [array size tcp_agents] }  { incr index } {
   puts "Setting up tcp agent $index"
   $ns attach-agent $n($index) $tcp_agents($index)
   $cbr_i($index) set rate_ 0.5Mbps
   $cbr_i($index) attach-agent $tcp_agents($index)
   $tcp_agents($index) set class_ $index
   $tcp_agents($index) set tcpTick_ 0.01
   $tcp_agents($index) set add793slowstart_ true
   $tcp_agents($index) set cwmax_ 40
}

$tcp_agents(2) set v_alpha_ 3
$tcp_agents(2) set v_beta_ 6

# Node 3: No settings
#$ns queue-limit $n(0) $n(3) 20
#$ns queue-limit $n(1) $n(3) 20
#$ns queue-limit $n(2) $n(3) 20
$ns queue-limit $n(3) $n(4) 20

# Node 4: 3 Sinks, one for each tcp agent
# Connect TCP to sinks
for { set index 0 }  { $index < [array size tcp_agents] }  { incr index } {
    set null($index) [new Agent/TCPSink]
    $ns attach-agent $n(4) $null($index)
    $ns connect $tcp_agents($index) $null($index)
    $tcp_agents($index) attach-trace $nff
}

for { set index 0 }  { $index < 20 }  { incr index 2 } {
    set end [expr {$index + 1}]
    $ns at $index "$cbr_i(1) start"
    $ns at $end "$cbr_i(1) stop"
    puts "Starting n1 at $index and stopping it at $end"
}

for { set index 0 }  { $index < 20 }  { incr index } {
    set end [expr {$index + 0.5}]
    $ns at $index "$cbr_i(0) start"
    $ns at $end "$cbr_i(0) stop"
    puts "Starting n0 at $index and stopping it at $end"
}

for { set index 0 }  { $index < 20 }  { incr index 4 } {
    set end [expr {$index + 2}]
    $ns at $index "$cbr_i(2) start"
    $ns at $end "$cbr_i(2) stop"
    puts "Starting n2 at $index and stopping it at $end"
}


$ns at 0.0 "recordTCPTimes"
$ns at 20.0 "finish"

$ns run


