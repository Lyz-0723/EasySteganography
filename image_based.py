import numpy as np
from PIL import Image


def encode_message(message: str):
    return [format(ord(x), '08b') for x in message]


def decode_message(message_list: list[str]):
    return "".join([chr(int(x, 2)) for x in message_list])


def odd_to_even(num: int):
    return num - 1 if num % 2 != 0 else num


def even_to_odd(num: int):
    return num - 1 if num % 2 == 0 else num


def modify_pixel(pixels: np.array, bin_message: str, last: bool):
    for j in range(len(bin_message)):
        x = j // 3
        y = j % 3

        if bin_message[j] == '0':
            pixels[x][y] = odd_to_even(pixels[x][y])

        if bin_message[j] == '1':
            pixels[x][y] = abs(even_to_odd(pixels[x][y]))

    if last:
        pixels[-1][-1] = abs(even_to_odd(pixels[-1][-1]))
    else:
        pixels[-1][-1] = odd_to_even(pixels[-1][-1])


def image_array_reshape(image: Image):
    pixels = np.array(image)
    shape = pixels.shape

    pixels = pixels.reshape(shape[0] * shape[1], shape[2])

    return pixels, shape


def encode_image(image: Image, bin_message_list: str):
    bin_message_list = encode_message(bin_message_list)

    pixels, shape = image_array_reshape(image)

    for i in range(len(bin_message_list)):
        last = i == (len(bin_message_list) - 1)

        try:
            start = i * 3
            modify_pixel(pixels[start: start + 3], bin_message_list[i], last)
        except IndexError:
            print('Message is too long')

    return Image.fromarray(pixels.reshape(shape))


def encode_and_save(img_path: str, save_directory: str, save_name: str, message: str):
    image_copy = Image.open(img_path, 'r').copy()

    new_img = encode_image(image_copy, message)

    new_img.save(f"{save_directory}/{save_name}", 'PNG')


def get_binstr(data: list[str], pixels: np.array):
    pixels = pixels.reshape(9,)

    binstr = ''
    for i in range(len(pixels) - 1):
        binstr += '0' if pixels[i] % 2 == 0 else '1'

    data.append(binstr)
    return True if pixels[-1] % 2 == 1 else False


def decode_image(img_path: str):
    image = Image.open(img_path, 'r')

    pixels, _ = image_array_reshape(image)

    data = []
    i = 0
    while True:
        start = i * 3
        end_of_message = get_binstr(data, pixels[start: start + 3])

        if end_of_message:
            break

        i += 1

    return decode_message(data)
