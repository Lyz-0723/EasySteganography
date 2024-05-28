import cv2

import numpy as np


def modify_pixel(pixels: np.array, bin_messages: str):
    print(pixels[:5])
    r_channel = list(pixels[:, 0])
    g_channel = list(pixels[:, 1])
    b_channel = list(pixels[:, 2])

    r_fft = np.fft.fft(r_channel)
    g_fft = np.fft.fft(g_channel)
    b_fft = np.fft.fft(b_channel)

    # Hide messages in freq domain
    for i in range(len(bin_messages)):
        _ = 1


def get_hidden_messages(pixels: np.array):
    _ = 1
