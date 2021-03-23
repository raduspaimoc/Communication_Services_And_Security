# Scenario script
# Authors:
# Lluís Mas & Radu Spaimoc

# Files to store trace and metrics
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
proc record_tcp_times { } {
	
	global ns tcp_agents nff cbr_i
	
	set now [$ns now]
	
    for { set index 0 }  { $index < [array size tcp_agents] }  { incr index } {
        write_agent_metrics $tcp_agents($index) $index $nff $now
    }

	$ns at [expr $now+0.1] "recordTCPTimes"
}

# Procedure to recrod CWND metrics
proc write_agent_metrics { tcp n nff now args } {
    set rtt  [expr [$tcp set rtt_]  * [$tcp set tcpTick_]]
    set srtt  [expr ([$tcp set srtt_] >> [$tcp set T_SRTT_BITS]) * [$tcp set tcpTick_]]
    set rttvar  [expr ([$tcp set rttvar_] >> [$tcp set T_RTTVAR_BITS]) * [$tcp set tcpTick_]]
    set bo [expr [$tcp set backoff_]]
    set cwnd  [expr [$tcp set cwnd_]]
    set cwmax  [expr [$tcp set cwmax_]]
    puts $nff "$n $now $rtt $srtt $cwnd $cwmax [expr 0.5*($bo-1)]"
}


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


$ns at 0.0 "record_tcp_times"
$ns at 20.0 "finish"

$ns run


