import numpy as np


def modify_pixel(pixels: np.array, bin_messages: str):
    pos = 0
    tun = 0

    # Encode the messages
    for i in range(len(bin_messages)):
        if bin_messages[i] == '0':
            pixels[tun][pos] = pixels[tun][pos] - (1 if pixels[tun][pos] > 0 else -1) if \
                pixels[tun][pos] % 2 == 1 else pixels[tun][pos]
        else:
            pixels[tun][pos] = pixels[tun][pos] - (1 if pixels[tun][pos] > 0 else -1) if \
                pixels[tun][pos] % 2 == 0 else pixels[tun][pos]
        pos += 1
        if pos == 3:
            pos = 0
            tun += 1

    # Set the end of the messages
    for i in range(8):
        if pixels[tun][pos] % 2 == 1:
            pixels[tun][pos] = pixels[tun][pos] - (1 if pixels[tun][pos] > 0 else -1)
        pos += 1
        if pos == 3:
            pos = 0
            tun += 1



def get_hidden_messages(pixels: np.array):
    messages = ''
    pos = 0
    tun = 0
    zero_count = 0

    for i in range(len(pixels)):
        messages += str(pixels[tun][pos] % 2)
        zero_count = zero_count + 1 if messages[-1] == '0' else 0
        if zero_count == 8:
             break
        pos += 1
        if pos == 3:
            pos = 0
            tun += 1

    messages = messages[:-8]
    messages = [messages[i:i+8] for i in range(0, len(messages), 8)]
    return messages
