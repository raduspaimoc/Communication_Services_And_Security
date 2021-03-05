import sys
import os


def create_packets_list(lines):
    packets = []
    for line in lines:
        lst = line.replace('[', "").replace(']', "").strip().split(",")
        packets.append([float(lst[0]), float(lst[1]), int(lst[2])])
    return packets


def read_file(file_name):
    file = open(file_name, 'r')
    lines = file.readlines()
    return create_packets_list(lines)


def wfq(packets, flows, flows_band, estimated_time_to_finish=0.0, recived_packets=[]):

    # Estimated time to finish: Fi = max(F' , Ai ) + Pi · rj

    for packet in packets:
        arrival_time = packet[0]
        packet_length = packet[1]
        flow = packet[2]

        packet_estimated_time_to_finish = max(estimated_time_to_finish, arrival_time) + (packet_length * flows_band[flow - 1])
        if arrival_time <= estimated_time_to_finish:
            # [Arrival time(float), Packet length(float), Flow / stream identifier(integer ≥ 1)], packet_estimated_time_to_finish
            recived_packets.append(packet + [packet_estimated_time_to_finish])
    print(recived_packets)


if __name__ == '__main__':

    # Test files strucutre:
    # [Arrival time(float), Packet length(float), Flow / stream identifier(integer ≥ 1)]

    # Solutions
    # Test 1 solution: [3, 2, 1, 4, 8, 5, 6, 7, 11, 12, 9, 10, 14, 15, 13]
    # Test 2 solution: [3, 1, 9, 5, 8, 12, 13, 11, 15, 2, 10, 14, 6, 4, 7]
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