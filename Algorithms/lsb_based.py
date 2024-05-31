import numpy as np


def modify_pixel(pixels: np.array, bin_message: list[str]):
    for i in range(len(bin_message)):
        pixel_slice = pixels[i * 3: i * 3 + 3]

        for j in range(len(bin_message[i])):
            x = j // 3
            y = j % 3

            pixel_slice[x][y] = (pixel_slice[x][y] & 254) | int(bin_message[i][j])

        pixel_slice[-1][-1] = (pixel_slice[-1][-1] & 254) | (1 if i == (len(bin_message) - 1) else 0)


def get_bin_value(value: int):
    return str(value & 1)


def get_hidden_messages(pixels: np.array, position: str):
    secret = ''
    pos = 0
    while True:
        flat_pixel = pixels[pos * 3: pos * 3 + 3].reshape(9, )

        secret += ''.join(get_bin_value(x) for x in flat_pixel[:8])

        if flat_pixel[-1] % 2 == 1:
            break
        pos += 1

    return [secret[i:i + 8] for i in range(0, len(secret), 8)]
