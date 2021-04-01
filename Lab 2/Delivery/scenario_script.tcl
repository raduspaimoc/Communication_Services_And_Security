# Scenario script
# Authors:
# Lluís Mas & Radu Spaimoc

# Simulator object creation
set ns [new Simulator]

# Trace Output files for trace and cwnd
set outputfile "trace"
set tfile [open $outputfile.tr w]
$ns trace-all $tfile
set rfile [open $outputfile.rtt w]

# Prcedure to connect TCP node to sink
proc node_to_sink { agent } {
    global ns tcp_agents n rfile

    set null($agent) [new Agent/TCPSink]
    $ns attach-agent $n(4) $null($agent)
    $ns connect $tcp_agents($agent) $null($agent)
    $tcp_agents($agent) attach-trace $rfile
}

# Procedure to setup agents
proc agent_setup { index } {
    global ns n tcp_agents cbr_i

    puts "Setting up tcp agent $index"

    $ns attach-agent $n($index) $tcp_agents($index)
    $cbr_i($index) set rate_ 0.5Mbps
    $cbr_i($index) attach-agent $tcp_agents($index)
    $tcp_agents($index) set class_ $index
    $tcp_agents($index) set tcpTick_ 0.01
    $tcp_agents($index) set cwmax_ 40
    $tcp_agents($index) set add793slowstart_ true
}

# Procedure to record TCP times
proc record_tcp_times { } {

	global ns tcp_agents rfile cbr_i

	set now [$ns now]

    for { set index 0 }  { $index < [array size tcp_agents] }  { incr index } {
        write_agent $tcp_agents($index) $index $rfile $now
    }

	$ns at [expr $now+0.1] "record_tcp_times"
}

# Procedure to logg multiple values
proc write_agent { tcp n rfile now args } {
    set rtt  [expr [$tcp set rtt_]  * [$tcp set tcpTick_]]
    set srtt  [expr ([$tcp set srtt_] >> [$tcp set T_SRTT_BITS]) * [$tcp set tcpTick_]]
    set rttvar  [expr ([$tcp set rttvar_] >> [$tcp set T_RTTVAR_BITS]) * [$tcp set tcpTick_]]
    set bo [expr [$tcp set backoff_]]
    set cwnd  [expr [$tcp set cwnd_]]
    set cwmax  [expr [$tcp set cwmax_]]
    puts $rfile "$n $now $rtt $srtt $cwnd $cwmax [expr 0.5*($bo-1)]"
}

# Finishing procedure
proc finish {} {
    global ns tfile rfile
    $ns flush-trace
    close $tfile
    close $rfile
    exit 0
}


# Nodes creation
#
#  n3
#     \
#      \
#  n2--n3--------n4
#      /
#     /
#  n1

set n(0) [$ns node]
set n(1) [$ns node]
set n(2) [$ns node]
set n(3) [$ns node]
set n(4) [$ns node]

# TCP agents (Default TCP agent: Tahoe)
set tcp_agents(0) [new Agent/TCP]
set tcp_agents(1) [new Agent/TCP/Reno]
set tcp_agents(2) [new Agent/TCP/Vegas]

# Traffic CBR
set cbr_i(0) [new Application/Traffic/CBR]
set cbr_i(1) [new Application/Traffic/CBR]
set cbr_i(2) [new Application/Traffic/CBR]

# Duplex lines between nodes
$ns duplex-link $n(2) $n(3) 5Mb 20ms DropTail
$ns duplex-link $n(1) $n(3) 5Mb 20ms DropTail
$ns duplex-link $n(0) $n(3) 5Mb 20ms DropTail
$ns duplex-link $n(3) $n(4) 1Mb 50ms DropTail

# Node0 --->
# Vars: CWMAX: 40 & tcpTick: 0.01
for { set i 0 }  { $i < [array size tcp_agents] }  { incr i } {
   agent_setup $i
}

# Node2 --->
# Setting state Vars
$tcp_agents(2) set v_alpha_ 3
$tcp_agents(2) set v_beta_ 6


# Node 3 --->
# Queue limit size: 20
$ns queue-limit $n(3) $n(4) 20

# Node 4 --->
# Connect TCP to sinks 1 foreach node
for { set agent 0 }  { $agent < [array size tcp_agents] }  { incr agent } {
    node_to_sink $agent
}

# Implementing scenario CBR activity

# TCP Vegas ---> Active: 2s - Paused: 2s
for { set index 0 }  { $index < 20 }  { incr index 4 } {
    set end [expr {$index + 2}]
    $ns at $index "$cbr_i(2) start"
    $ns at $end "$cbr_i(2) stop"
    puts "n2 actived at $index and stopped at $end."
}

# TCP Reno ---> Active: 1s - Paused: 1s
for { set index 0 }  { $index < 20 }  { incr index 2 } {
    set end [expr {$index + 1}]
    $ns at $index "$cbr_i(1) start"
    $ns at $end "$cbr_i(1) stop"
    puts "n1 actived at $index stopped at $end."
}

# TCP Tahoe ---> Active: 0.5s - Paused: 0.5s
for { set index 0 }  { $index < 20 }  { incr index } {
    set end [expr {$index + 0.5}]
    $ns at $index "$cbr_i(0) start"
    $ns at $end "$cbr_i(0) stop"
    puts "n0 actived at $index and stopped at $end."
}


$ns at 0.0 "record_tcp_times"
$ns at 20.0 "finish"

$ns run