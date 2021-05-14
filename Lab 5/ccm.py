def right_circular_shift(value):
    rotative_value = value & 0b00000001
    rotative_value = rotative_value << 7
    return (value >> 1) +  rotative_value

def double_right_circular_shift(value):
    return right_circular_shift(right_circular_shift(value))

key = 34
# the 0x53
x = 83

# We calculate the ctr 0
ctr0 = double_right_circular_shift(key)

ctr = [ctr0]

# now we calculate ctr 1 to ctr 5
for i in range(1, 5):
    ctr.append(double_right_circular_shift(ctr[i-1]) ^ x)

for ct in ctr:
    print('{0:08b}'.format(ct))


aes = [ct ^ key for ct in ctr]

info = '0000000000000001000000100000001100000100'

result = []
j=0
block_len = int(len(info) / len(aes))
for i in range(0, len(info), block_len):
    result.append(aes[j]^int(info[i:i+block_len], 2))
    j+=1
print('---AES XOR results---')
for ct in result:
    print('{0:08b}'.format(ct))

# MIC block
IV = int('00000000', 2)
#first block
first_block = (int(info[0:8], 2) ^ IV) ^ key

ccm = [first_block]
for i in range(8, len(info), block_len):
    ccm.append((int(info[i:i+8], 2)^ccm[-1])^key)

print('---MIC results---')
for cm in ccm:
    print('{0:08b}'.format(cm))
