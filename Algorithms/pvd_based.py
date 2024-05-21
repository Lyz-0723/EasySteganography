import math

import numpy as np


def modify_pixel(pixels: np.array, messages: str):
    # Encode datas into image
    pos = 0
    while len(messages) > 0:
        # Calculate the original difference about tunnel 0 and 1 in single pixel
        diff = abs(int(pixels[pos][0]) - int(pixels[pos][1]))
        # Calculate how many bits can this pixel encode
        bits = 0
        while 2 ** bits <= diff:
            bits += 1
        bits -= 1

        # If bits can be used in the pixel >0
        if bits > 0:
            # Check if the bits that can be used is more than the rest bits of message
            if bits <= len(messages):
                value = messages[:bits]
                messages = messages[bits:]
            else:
                bits = len(messages)
                value = messages
                messages = ''
            # Calculate the new tunnel value difference
            new_diff = 2 ** bits + int(value, 2)
            m = new_diff - diff
            # Set the new tunnel value
            if pixels[pos][0] > pixels[pos][1]:
                if pixels[pos][0] + math.ceil(m / 2) > 255:
                    pixels[pos][1] -= m
                elif pixels[pos][1] - math.floor(m / 2) < 0:
                    pixels[pos][0] += m
                else:
                    pixels[pos][0] += math.ceil(m / 2)
                    pixels[pos][1] -= math.floor(m / 2)
            else:
                if pixels[pos][0] - math.floor(m / 2) < 0:
                    pixels[pos][1] += m
                elif pixels[pos][1] + math.ceil(m / 2) > 255:
                    pixels[pos][0] -= m
                else:
                    pixels[pos][0] -= math.floor(m / 2)
                    pixels[pos][1] += math.ceil(m / 2)

        # Set bits with data's third tunnel to even number
        if pixels[pos][2] % 2 == 1:
            pixels[pos][2] -= 1 if pixels[pos][2] > 0 else -1
        pos += 1

    # Set one more bit's third tunnel to odd number for "end of message"
    if pixels[pos][2] % 2 == 0:
        pixels[pos][2] -= 1 if pixels[pos][2] > 0 else -1


def get_hidden_messages(pixels: np.array):
    secret_message = ''
    pos = 0
    # While pixel with message bits hiding not reaching the end
    while pixels[pos][2] % 2 == 0:
        bits = 0
        # Calculate difference of tunnel 0 and 1
        if pixels[pos][0] > pixels[pos][1]:
            diff = abs(pixels[pos][0] - pixels[pos][1])
        else:
            diff = abs(pixels[pos][1] - pixels[pos][0])
        # Calculate the bits hiding in current pixel
        while 2 ** bits <= diff:
            bits += 1
        bits -= 1

        # If the pixel are hiding some bits of message, get the bits data
        if bits > 0:
            diff -= (2 ** bits)
            str_part = str(bin(diff)[2:]).zfill(bits)
            secret_message += str_part

        pos += 1

    # Decode the message with ascii text
    binary_groups = [secret_message[i:i + 8] for i in range(0, len(secret_message), 8)]
    ascii_text = ''.join(chr(int(group, 2)) for group in binary_groups)
    return ascii_text

