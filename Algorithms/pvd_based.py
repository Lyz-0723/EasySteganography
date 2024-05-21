import math

import numpy as np


def modify_pixel(pixels: np.array, messages: str):
    pos = 0
    sum = 0
    while len(messages) > 0:
        diff = abs(int(pixels[pos][0]) - int(pixels[pos][1]))
        print(pos, diff, pixels[pos][0], pixels[pos][1])
        bits = 0

        while 2 ** bits <= diff:
            bits += 1
        bits -= 1

        if bits > 0:
            if bits <= len(messages):
                value = messages[:bits]
                messages = messages[bits:]
            else:
                bits = len(messages)
                value = messages
                messages = ''

            sum += bits
            print(bits)
            new_diff = 2 ** bits + int(value, 2)
            m = new_diff - diff

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
    print("Uses", pos, "pixels to hide data, total data length:", sum)

    print("Secret Data:", get_hidden_messages(pixels))


def get_hidden_messages(pixels: np.array):
    secret_message = ''
    pos = 0
    while pixels[pos][2] % 2 == 0:
        bits = 0
        print("Pos:", pos)
        if pixels[pos][0] > pixels[pos][1]:
            diff = abs(pixels[pos][0] - pixels[pos][1])
        else:
            diff = abs(pixels[pos][1] - pixels[pos][0])
        print(pixels[pos][0], pixels[pos][1], ", diff:", diff)
        while 2 ** bits <= diff:
            bits += 1
        bits -= 1
        print("Bits contain:", bits)
        if bits > 0:
            diff -= (2 ** bits)
            str_part = str(bin(diff)[2:]).zfill(bits)
            print("String part:", str_part)
            secret_message += str_part
        pos += 1
        print()
    print("Find", pos, "pixels hiding data, total data length:", len(secret_message))
    binary_groups = [secret_message[i:i + 8] for i in range(0, len(secret_message), 8)]
    ascii_text = ''.join(chr(int(group, 2)) for group in binary_groups)
    return ascii_text

