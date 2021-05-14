IV = 17
key = 34

data_icv = '000000010010001100100010'

# PS(0)
first_ps = key ^ IV

ps_bit = '{0:08b}'.format(first_ps)

ps = [ps_bit]
po = []
for i in range(1, len(data_icv)):
    first_bit = str(int(ps[i-1][4]) ^ int(ps[i-1][7]))
    ps.append(first_bit)
    po.append(first_bit)
    for j in range(1, 8):
        ps[i] += ps[i - 1][j-1]

po.append(ps[-1][0])


for i in range(len(ps)):
    print('PS('+str(i)+'): '+ps[i] + '  PO('+str(i)+'): '+po[i])



