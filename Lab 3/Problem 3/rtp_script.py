

def compute_rtp_missed_packets(file):
    file1 = open(file, 'r')
    Lines = file1.readlines()

    RTP_pack_missed = 0
    # Strips the newline character
    for line in Lines:
        if line.__contains__("RTP"):
            lst = line.split(' ')
            RTP_pack_missed += int(lst[5])

    return RTP_pack_missed


if __name__ == '__main__':

    pq_no_ping = compute_rtp_missed_packets('q4_pq_without_ping.txt')
    no_pq_no_ping = compute_rtp_missed_packets('q4_no_pq_without_ping.txt')
    pq_ping =  compute_rtp_missed_packets('q5_pq_with_ping.txt')
    no_pq_ping = compute_rtp_missed_packets('q5_no_pq_with_ping.txt')

    print("PQ - No Ping. RTP missed packets: ", pq_no_ping)
    print("NO PQ - No Ping. RTP missed packets: ", no_pq_no_ping)
    print("PQ - Ping. RTP missed packets: ", pq_ping)
    print("NO PQ - Ping. RTP missed packets: ", no_pq_ping)