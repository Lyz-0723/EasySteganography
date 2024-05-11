import numpy as np
from PIL import Image

from utils import encode_message, decode_message, image_array_reshape


def odd2even(num: int):
    return num - 1 if num % 2 != 0 else num


def even2odd(num: int):
    return num - 1 if num % 2 == 0 else num


def modify_pixel(pixels: np.array, bin_text: str, last: bool):
    for j in range(len(bin_text)):
        x = j // 3
        y = j % 3

        if bin_text[j] == '0':
            pixels[x][y] = odd2even(pixels[x][y])

        if bin_text[j] == '1':
            pixels[x][y] = abs(even2odd(pixels[x][y]))

    if last:
        pixels[-1][-1] = abs(even2odd(pixels[-1][-1]))
    else:
        pixels[-1][-1] = odd2even(pixels[-1][-1])


def encode_image(image: Image, message: str):
    bin_text_list = encode_message(message)

    pixels, shape = image_array_reshape(image)

    if len(bin_text_list) > len(pixels) // 3:
        print('Message is too long')
        return

    for i in range(len(bin_text_list)):
        last = i == (len(bin_text_list) - 1)

        start = i * 3
        modify_pixel(pixels[start: start + 3], bin_text_list[i], last)

    return Image.fromarray(pixels.reshape(shape))


def encode_and_save(img_path: str, save_directory: str, save_name: str, message: str):
    image_copy = Image.open(img_path, 'r').copy()

    new_img = encode_image(image_copy, message)

    new_img.save(f"{save_directory}/{save_name}", 'PNG')


def get_bin_text(data: list[str], pixels: np.array):
    pixels = pixels.reshape(9, )

    bin_text = ''
    for i in range(len(pixels) - 1):
        bin_text += '0' if pixels[i] % 2 == 0 else '1'

    data.append(bin_text)
    return True if pixels[-1] % 2 == 1 else False


def decode_image(img_path: str):
    image = Image.open(img_path, 'r')

    pixels, _ = image_array_reshape(image)

    data = []
    i = 0
    while True:
        start = i * 3

        if get_bin_text(data, pixels[start: start + 3]):
            break

        i += 1

    return decode_message(data)
