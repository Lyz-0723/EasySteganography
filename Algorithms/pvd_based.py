import math

import numpy as np


def modify_pixel(image: np.array, messages: str):
    pos = 0
    sum = 0
    while len(messages) > 0:
        diff = image[pos][0] - image[pos][1]
        bits = 0

        while 2 ** bits <= diff:
            bits += 1
        bits -= 1

        if bits <= len(messages):
            value = messages[:bits]
            messages = messages[bits:]
        else:
            bits = len(messages)
            value = messages
            messages = ''

        sum += bits
        if bits != 0:

            new_diff = 2 ** bits + int(value, 2)
            m = new_diff - diff

            if image[pos][0] > image[pos][1]:
                if image[pos][0] + math.ceil(m / 2) > 255:
                    image[pos][1] -= m
                elif image[pos][1] - math.floor(m / 2) < 0:
                    image[pos][0] += m
                else:
                    image[pos][0] += math.ceil(m / 2)
                    image[pos][1] -= math.floor(m / 2)
            else:
                if image[pos][0] - math.floor(m / 2) < 0:
                    image[pos][1] += m
                elif image[pos][1] + math.ceil(m / 2) > 255:
                    image[pos][0] -= m
                else:
                    image[pos][0] -= math.floor(m / 2)
                    image[pos][1] += math.ceil(m / 2)

        # Set bits with data's third tunnel to even number
        if image[pos][2] % 2 == 1:
            image[pos][2] -= 1 if image[pos][2] > 0 else -1
        pos += 1

    # Set one more bit's third tunnel to odd number for "end of message"
    if image[pos][2] % 2 == 0:
        image[pos][2] -= 1 if image[pos][2] > 0 else -1


def get_hidden_messages(image: np.array):
    secret_message = ''
    pos = 0
    while image[pos][2] % 2 == 0:
        bits = 0
        if image[pos][0] > image[pos][1]:
            diff = abs(image[pos][0] - image[pos][1])
        else:
            diff = abs(image[pos][1] - image[pos][0])

        while 2 ** bits <= diff:
            bits += 1
        bits -= 1

        if bits != 0:
            diff -= (2 ** bits)
            str_part = str(bin(diff)[2:]).zfill(bits)
            secret_message += str_part
        pos += 1

    binary_groups = [secret_message[i:i + 8] for i in range(0, len(secret_message), 8)]
    ascii_text = ''.join(chr(int(group, 2)) for group in binary_groups)
    return ascii_text

