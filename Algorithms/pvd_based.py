import math

import numpy as np

from utils import is_end


def set_value(pixels: np.array, pos: int, m: int):
    x = math.ceil(m / 2)
    y = math.floor(m / 2)

    def adjust_values(cond, idx1, idx2):
        nonlocal x, y
        while cond(pixels[pos][idx1] + x, pixels[pos][idx2] - y):
            x, y = (x - 1, y + 1) if pixels[pos][idx1] + x > 255 else (x + 1, y - 1)

        pixels[pos][idx1] += x
        pixels[pos][idx2] -= y

    if pixels[pos][0] > pixels[pos][1]:
        adjust_values(lambda a, b: a > 255 or b < 0, 0, 1)
    else:
        adjust_values(lambda a, b: a > 255 or b < 0, 1, 0)


def modify_pixel(pixels: np.array, bin_message: str, position: str):
    is_end(pixels, position)

    # Encode datas into image
    pos = 0
    while len(bin_message) > 0:
        # Calculate the original difference about tunnel 0 and 1 in single pixel
        diff = abs(int(pixels[pos][0]) - int(pixels[pos][1]))

        # Calculate how many bits can this pixel encode
        bits = 0 if diff == 0 else math.floor(math.log2(diff))

        # If bits can be used in the pixel >0
        if bits > 0:
            # Check if the bits that can be used is more than the rest bits of message
            if bits <= len(bin_message):
                value = bin_message[:bits]
                bin_message = bin_message[bits:]
            else:
                bits = len(bin_message)
                value = bin_message
                bin_message = ''

            # Calculate the new tunnel value difference
            new_diff = 2 ** bits + int(value, 2)
            m = new_diff - diff

            # Set the new tunnel value
            set_value(pixels, pos, m)

        # Set bits with data's third tunnel to even number
        pixels[pos][2] = (pixels[pos][2] & 254) | 0
        pos += 1

    # Set one more bit's third tunnel to odd number for "end of message"
    pixels[pos][2] = (pixels[pos][2] & 254) | 1

    is_end(pixels, position)


def get_hidden_messages(pixels: np.array, position: str):
    is_end(pixels, position)

    secret = ''
    pos = 0
    # While pixel with message bits hiding not reaching the end
    while pixels[pos][2] % 2 == 0:

        # Calculate difference of tunnel 0 and 1
        diff = abs(int(pixels[pos][0]) - int(pixels[pos][1]))

        # Calculate the bits hiding in current pixel
        bits = 0 if diff == 0 else math.floor(math.log2(diff))

        # If the pixel are hiding some bits of message, get the bits data
        if bits > 0:
            diff -= (2 ** bits)
            str_part = format(diff, '0' + str(bits) + 'b')
            secret += str_part

        pos += 1

    # Decode the message with ascii text
    return [secret[i:i + 8] for i in range(0, len(secret), 8)]
