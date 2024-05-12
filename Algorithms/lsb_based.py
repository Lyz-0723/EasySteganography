import numpy as np


def modify_pixel(pixels: np.array, bin_text: str, last: bool):
    for j in range(len(bin_text)):
        x = j // 3
        y = j % 3

        pixels[x][y] = (pixels[x][y] & 254) | int(bin_text[j])

    pixels[-1][-1] = (pixels[-1][-1] & 254) | (1 if last else 0)


def get_bin_value(value: int):
    return str(value & 1)
