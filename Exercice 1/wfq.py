import sys
import os

transmission_order_sequence = []

def create_packets_list(lines):
    packets = []
    packet_num = 1
    for line in lines:
        lst = line.replace('[', "").replace(']', "").strip().split(",")
        packets.append([packet_num, float(lst[0]), float(lst[1]), int(lst[2])])
        packet_num += 1

    # Structure
    # [Packet Num, Arrival time(float), Packet length(float), Flow / stream identifier(integer ≥ 1)]
    return packets


def read_file(file_name):
    file = open(file_name, 'r')
    lines = file.readlines()
    return create_packets_list(lines)


def search_first_packet_to_complete(packets):
    if len(packets) == 0:
        exit()
    packet_to_complete = packets[0]
    estimated_time = packet_to_complete[4]

    for packet in packets:
        if packet[4] < estimated_time:
            estimated_time = packet[4]
            packet_to_complete = packet
    return packet_to_complete


def wfq(packets, flows, flows_band, estimated_time_to_finish=0.0, received_packets=[]):

    # Estimated time to finish: Fi = max(F' , Ai ) + Pi · rj

    packets_to_remove = []
    for packet in packets:
        arrival_time = packet[1]
        packet_length = packet[2]
        flow = packet[3]

        packet_estimated_time_to_finish = max(estimated_time_to_finish, arrival_time) + (packet_length * (100 / flows_band[flow - 1]))
        if arrival_time <= estimated_time_to_finish:
            # [Arrival time(float), Packet length(float), Flow / stream identifier(integer ≥ 1)], packet_estimated_time_to_finish
            received_packets.append(packet + [packet_estimated_time_to_finish])
            packets_to_remove.append(packet)

    # Remove packets received from all packets list
    packets = [packet for packet in packets if packet not in packets_to_remove]

    packet = search_first_packet_to_complete(received_packets)
    packet_length = packet[2]

    transmission_order_sequence.append(packet[0])
    received_packets.remove(packet)
    print("WFQ Transmission sequence: ", transmission_order_sequence)

    wfq(packets, flows, flows_band, estimated_time_to_finish= estimated_time_to_finish + packet_length, received_packets=received_packets)


if __name__ == '__main__':

    # Test files strucutre:
    # [Arrival time(float), Packet length(float), Flow / stream identifier(integer ≥ 1)]

    # Tests parameters
    # Test 1 params: 4 25 50 12.5 12.5 Test1.txt
    # Test 2 params: 4 50 12.5 25 12.5 Test2.txt
    # Test 3 params: 4 25 50 12.5 12.5 Test3.txt



    # Tests Solutions
    # Test 1 solution: [3, 2, 1, 8, 6, 11, 12, 14, 9, 5, 13, 4, 10, 15, 7]
    # Test 2 solution: [1, 10, 15, 17, 11, 20, 14, 12, 7, 21, 18, 6, 2, 24, 25, 13, 9, 16, {3,4,23}, {5,8,22}, 19]
    # Test 3 solution: [2, 9, 6, 10, 13, 8, 11, 15, 14, 5, 3, 1, 4, 7, 12]

    # Script params
    # 1 Total number of flow
    # 2 - n Fraction of the bandwidth assigned to each flow (as a percentage)
    # n + 1 File name containing the list of triplets to be scheduled

    if len(sys.argv) <= 1:
        sys.exit("Use: %s <number_of_flow> <bandwith_frac_per_flow> <file_name>" % sys.argv[0])

    if os.path.isfile(sys.argv[-1]):
       file_name = os.path.abspath(sys.argv[-1])
    else:
        sys.exit("Error! %s not found" % sys.argv[-1])

    num_of_flow = int(sys.argv[1])
    flow_bandwith_frac = [float(i) for i in sys.argv[2 : len(sys.argv) - 1]]
    packets = read_file(file_name)

    print("Num of flow: " , str(num_of_flow))
    print("Bandwith frac per flow: ", flow_bandwith_frac)
    print("Num packets in sqeuence: ", len(packets))

    wfq(packets, num_of_flow, flow_bandwith_frac)