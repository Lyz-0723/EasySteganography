import numpy as np
from PIL import Image


def encode_message(message: str) -> list[str]:
    return [format(ord(x), '08b') for x in message]


def decode_message(message_list: list[str]) -> str:
    return "".join([chr(int(x, 2)) for x in message_list])


def image_array_reshape(image: Image) -> tuple[np.array, type(tuple)]:
    pixels = np.array(image)
    shape = pixels.shape

    pixels = pixels.reshape(shape[0] * shape[1], shape[2])

    return pixels, shape


def text_fits_in_image(pixels: np.array, text: str) -> bool:
    return len(text) <= len(pixels) // 3
