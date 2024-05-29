import cv2

import numpy as np


def modify_pixel(pixels: np.array, bin_messages: str):
    print(bin_messages)
    r_channel = pixels[:, 0].astype(float)
    b_channel = pixels[:, 2].astype(float)

    r_fft = np.fft.fft(r_channel)
    b_fft = np.fft.fft(b_channel)

    # Hide messages in frequency domain
    for i in range(len(bin_messages)):
        r_real = np.real(r_fft[i])
        r_imag = np.imag(r_fft[i])
        b_real = np.real(b_fft[i])
        b_imag = np.imag(b_fft[i])
        if bin_messages[i] == '1':
            r_fft[i] = (r_real - 1 + 1j * r_imag) if (int(r_real) % 2 == 0) else r_fft[i]
        else:
            r_fft[i] = (r_real - 1 + 1j * r_imag) if (int(r_real) % 2 == 1) else r_fft[i]
        b_fft[i] = (b_real - 1 + 1j * b_imag) if (int(b_real) % 2 == 1) else b_fft[i]
        print(int(np.real(b_fft[i])) % 2, end='')

    # Set the end of the message
    pos = len(bin_messages)
    b_real = np.real(b_fft[pos])
    b_imag = np.imag(b_fft[pos])
    b_fft[pos] = (b_real - 1 + 1j * b_imag) if (int(b_real) % 2 == 0) else b_fft[pos]
    r_channel_rev = np.fft.ifft(r_fft).real
    b_channel_rev = np.fft.ifft(b_fft).real

    pixels[:, 0] = r_channel_rev
    pixels[:, 2] = b_channel_rev

    print("Msg:", get_hidden_messages(pixels))


def get_hidden_messages(pixels: np.array):
    # Extract red and blue channels
    r_channel = pixels[:, 0].astype(float)
    b_channel = pixels[:, 2].astype(float)
    r_fft = np.fft.fft(r_channel)
    b_fft = np.fft.fft(b_channel)
    messages = ''

    # Check the first 50 pixels' data -> 1 for message end
    print()
    [print(int(np.real(b_fft[i])) % 2, end='') for i in range(50)]

    # Extract hidden messages from frequency domain
    for i in range(50):  # Check first 50 pixels data
        # b_real = np.real(b_fft[i])
        # if int(b_real) % 2 == 1:  # Check if it's the end of the message
        #     break
        r_real = np.real(r_fft[i])
        messages += '1' if int(r_real % 2) == 1 else '0'

    return messages
