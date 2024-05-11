import numpy as np

from utils import odd2even, even2odd


def modify_pixel(pixels: np.array, bin_text: str, last: bool):
    for j in range(len(bin_text)):
        x = j // 3
        y = j % 3

        pixels[x][y] = int(format(pixels[x][y], "08b")[:-1] + bin_text[j], 2)

    if last:
        pixels[-1][-1] = abs(even2odd(pixels[-1][-1]))
    else:
        pixels[-1][-1] = odd2even(pixels[-1][-1])


def get_bin_text(data: list[str], pixels: np.array):
    pixels = pixels.reshape(9, )

    bin_text = ''
    for i in range(len(pixels) - 1):
        bin_text += format(pixels[i], "08b")[-1]

    data.append(bin_text)
    return pixels[-1] % 2 == 1
