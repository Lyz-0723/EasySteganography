import numpy as np


def modify_pixel(pixels: np.array, bin_message: str):
    pos = 0
    tun = 0

    # Encode the messages
    for i in range(len(bin_message)):
        pixels[tun][pos] = (pixels[tun][pos] & 254) | int(bin_message[i])

        pos += 1
        tun += pos // 3
        pos = pos % 3

    # Set the end of the messages
    for i in range(8):
        pixels[tun][pos] = (pixels[tun][pos] & 254) | 0

        pos += 1
        tun += pos // 3
        pos = pos % 3


def get_hidden_messages(pixels: np.array):
    secret = ''
    zero_count = 0

    for i in range(len(pixels)):
        tun = i // 3
        pos = i % 3

        secret += str(pixels[tun][pos] % 2)
        zero_count = zero_count + 1 if secret[-1] == '0' else 0

        if zero_count == 8:
            break

    return [secret[i:i + 8] for i in range(0, len(secret) - 8, 8)]
