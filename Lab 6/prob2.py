
def hex_to_bin(hexdec):
    """Convert hexadecimal to binary."""
    dec = int(hexdec, 16)
    binary_result = bin(dec)
    return binary_result[2:]


def xor(num1, num2):
    """XOR two binary numbers."""
    # Same bit = 0 diferent bit = 1
    y = int(num1, 2)^int(num2,2)

    max_size = max(len(num1),len(num2))
    xor_result = bin(y)[2:].zfill(max_size)

    return xor_result


def shift(list, n=0):
    """Shift elements of a list by n steps"""
    return list[-n:]+list[:-n]


def generate_information_blocks(information, length_block): 
    """
    Split the information in blocks of a length of the length_block value
    
    Arguments:
        information -- Information to be splited
        length_block -- length of the blocks

    Returns:
        info_blocks = Array of blocks of information
    """

    info_blocks = []
    for index in range(0,len(information),length_block):
        info_blocks.append(information[index:index+length_block])
    return info_blocks


def generate_counter_blocks(info_blocks, key):
    """
    ctr(0) = key ≫ 2
    For each infornation block, in the first iteration, the ctr will be the key with a circular shift to the right of 2 values.
    
    ctr(i) = ctr(i−1)≫2 XOR 0x53, i>0
    For the others iterations the ctr will be the previous ctr with a circular shift to the right of 2 values and an xor of this result with "0x53".

    Arguments:
        info_blocks -- Blocks of information
        key -- key used

    Returns:
        counter_blocks = an Array of counter blocks calculated (ctr)
    """
    counter_blocks = []
    xor_key = hex_to_bin("0x53").zfill(8)

    for i in range(len(info_blocks)):

        if i == 0:
            # ctr(0) = key ≫ 2
            counter_blocks.append(shift(key, 2))

        else:
            # ctr(i) = ctr(i−1)≫2 XOR 0x53, i>0
            prev_shift = shift(counter_blocks[i-1], 2)
            counter_blocks.append(xor(prev_shift, xor_key))
             
    return counter_blocks


def CTR_operation(info_blocks, counter_blocks, key):
    """
    For each information block, calculate the AES(xor) between the key and their corresponding ctr 
    and then, calculate the xor between the obtained result and the block of information

    Arguments:
        info_blocks -- Blocks of information
        counter_blocks -- the differents ctr
        key -- key used

    Returns:
        information_result = an Array of the CTR operations results
    """

    information_result = []

    for i in range(len(counter_blocks)):
        AES_simulation = xor(counter_blocks[i], key)
        information_result.append(xor(AES_simulation, info_blocks[i]))
    
    return information_result


def CTR_process(information, key):
    """
    Arguments:
        Information -- Information to be proecessed
        key -- key used

    Returns:
        A String of the CTR operations results
    """
    # Generate information blocks
    info_blocks = generate_information_blocks(information, length_block)

    # Calculate the differents ctr
    counter_blocks = generate_counter_blocks(info_blocks, key) 

    # CTR operation
    information_result = CTR_operation(info_blocks, counter_blocks, key)
    
    return "".join(information_result)


def generate_MIC(information, key, IV):
    """Generate MIC (Message Integrated Check)
        First iteration -> xor of the first block information with the IV, calculate AES of the result obtained with the key.
        Others iterations -> xor of the block information with the result acumulated, calculate AES of the result obtained with the key.
    """

    # Generate information blocks
    info_blocks = generate_information_blocks(information, length_block)

    # Initialize the result to IV
    result = IV
    for info_block in info_blocks:
        # xor of the last result with the block of information
        result = xor(info_block,result)

        # xor of the result obtained with the key (AES result with key)
        result = xor(result,key)   
    
    return result


def CCMP_process(information, length_block, key, IV, decipher_mode):
    """
    Arguments:
        information -- information to be deciphered
        length_block  -- length of the information blocks
        key  -- Key used
        IV  -- Initialized to 0
        decipher_mode -- Indicates if cipher or decipher

    Returns:
        CTR_result -- information ciphered or deciphered
        generated_MIC -- MIC generated
    """

    # CTR
    CTR_result = CTR_process(information, key)

    # CBC
    if not decipher_mode: 
        # Calculate MIC with the information
        generated_MIC = generate_MIC(information, key, IV)
    else:
        # Calculate MIC with the information deciphered
        generated_MIC = generate_MIC(CTR_result, key, IV)

    return CTR_result, generated_MIC


def validation(event, generated, expected):
    """Validation to check that generated is equal to expected."""

    print(event, " generated: " + str(generated) + ", expected: " + expected)
    print(event, " SUCCESS: " + str(generated == expected))


if __name__ == "__main__":
    #Variables initialization. zfill(x) Fill the strings with zeros until they are x characters long 
    length_block = 8
    key = hex_to_bin("0x22").zfill(8)
    information = hex_to_bin("0x0001020304").zfill(40)
    IV = hex_to_bin("0x0").zfill(8)
    
    #Expected values
    expected_ciphered = hex_to_bin("0xAA522FB151")
    expected_MIC = hex_to_bin("0x26").zfill(8)

    print("key: " + key)
    print("information: " + information)
    print("IV: " + IV)
    print("expected_ciphered: " + expected_ciphered)
    print("expected_MIC: " + expected_MIC)

    # Cipher the information
    decipher_mode = False
    ciphered_info, cipher_generated_MIC = CCMP_process(information, length_block, key, IV, decipher_mode)

    # Decipher the information
    decipher_mode = True
    decipher_info, decipher_generated_MIC = CCMP_process(ciphered_info, length_block, key, IV, decipher_mode)


    print("\nCipher validation")
    # Validate that the ciphered information is equal to the ciphered information expected (0xAA522FB151)
    validation("Cipher info", ciphered_info, expected_ciphered)
    # Validate that the cipher generated MIC is equal to the MIC expected (0x22)
    validation("Cipher MIC", cipher_generated_MIC, expected_MIC)


    print("\nDecipher validation")
    # Validate that the deciphered information is equal to the information before being ciphered
    validation("Decipher info", decipher_info, information)
    # Validate that the decipher generated MIC is equal to the cipher generated MIC
    validation("Decipher MIC", decipher_generated_MIC, cipher_generated_MIC)
