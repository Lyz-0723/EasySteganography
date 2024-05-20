import math

import numpy as np


def modify_pixel(image: np.array, messages: str):
    print(messages, len(messages))
    pos = 0
    sum = 0
    while len(messages) > 0:
        # print("origin:", image[pos][0], image[pos][1])
        diff = abs(image[pos][0] - image[pos][1])
        bits = 0

        while 2 ** bits <= diff:
            bits += 1
        bits -= 1

        # print(bits, len(messages))
        if bits <= len(messages):
            value = messages[:bits]
            messages = messages[bits:]
        else:
            bits = len(messages)
            value = messages
            messages = ''

        sum += bits
        if value == '':
            pos += 1
            continue

        new_diff = 2 ** bits + int(value, 2)
        m = new_diff - diff
        print(diff)

        if image[pos][0] >= image[pos][1]:
            image[pos][0] += math.ceil(m / 2)
            image[pos][1] -= math.floor(m / 2)
        else:
            image[pos][0] -= math.floor(m / 2)
            image[pos][1] += math.ceil(m / 2)
        # print("new:", image[pos][0], image[pos][1], '\n')

        pos += 1
        # Set bits with data's third tunnel to even number
        if image[pos][2] % 2 == 1:
            image[pos][2] -= 1 if image[pos][2] > 0 else -1

    # Set one more bit's third tunnel to odd number for "end of message"
    if image[pos][2] % 2 == 0:
        image[pos][2] -= 1 if image[pos][2] > 0 else -1
    print("sum:", sum)
    get_hidden_messages(image)


def get_hidden_messages(image: np.array):
    secret_message = ''
    pos = 0
    while image[pos][2] % 2 == 0:
        bits = 0
        # print(image[pos][0] - image[pos][1])
        if image[pos][0] > image[pos][1]:
            diff = abs(image[pos][0] - image[pos][1])
        else:
            diff = abs(image[pos][1] - image[pos][0])
        print("diff:", diff)

        while 2 ** bits <= diff:
            bits += 1
        bits -= 1

        diff -= (2 ** bits)
        str_part = str(bin(diff)[2:]).zfill(bits)
        secret_message += str_part
        print("pos, str_part:", pos, str_part)
        pos += 1

    binary_groups = [secret_message[i:i + 8] for i in range(0, len(secret_message), 8)]
    ascii_text = ''.join(chr(int(group, 2)) for group in binary_groups)
    print(secret_message)
    print(ascii_text, len(ascii_text))
    return ascii_text

