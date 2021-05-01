

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

    first = compute_rtp_missed_packets('1000000_400000_400000.txt')
    second = compute_rtp_missed_packets('1000000_40000_40000.txt')
    third = compute_rtp_missed_packets('1000000_4000_4000.txt')

    fourth = compute_rtp_missed_packets('800000_400000_400000.txt')
    fifth = compute_rtp_missed_packets('800000_40000_40000.txt')
    sixth = compute_rtp_missed_packets('800000_4000_4000.txt')

    seventh = compute_rtp_missed_packets('500000_400000_400000.txt')
    eigth = compute_rtp_missed_packets('500000_40000_40000.txt')
    ninth = compute_rtp_missed_packets('500000_4000_4000.txt')


    print("1000000_400000_400000 LOST FRAMES: ", first)
    print("1000000_40000_40000 LOST FRAMES: ", second)
    print("1000000_4000_4000 LOST FRAMES: ", third)
    print("800000_400000_400000 LOST FRAMES: ", fourth)
    print("800000_40000_40000 LOST FRAMES: ", fifth)
    print("800000_4000_4000 LOST FRAMES: ", sixth)
    print("500000_400000_400000 LOST FRAMES: ", seventh)
    print("500000_40000_40000 LOST FRAMES: ", eigth)
    print("500000_4000_4000 LOST FRAMES: ", ninth)