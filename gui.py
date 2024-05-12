from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow
from PIL import Image
import numpy as np
from utils import encode_message, decode_message, image_array_reshape, text_fits_in_image

from Algorithms import lsb_based


def get_bin_text(data: list[str], pixels: np.array, algorithm: str, position: str):
    pixels = pixels.reshape(9, )
    bin_text = ''
    for i in range(8):
        match algorithm:
            case "LSB steg":
                bin_text += lsb_based.get_bin_value(pixels[i])
            case _:
                bin_text += lsb_based.get_bin_value(pixels[i])

    data.append(bin_text)
    return pixels[-1] % 2 == 1


def encode_image(image: Image, message: str, algorithm: str, position: str):
    bin_text_list = encode_message(message)
    pixels, shape = image_array_reshape(image)

    if not text_fits_in_image(pixels, message):
        print('Message is too long')
        return

    for i in range(len(bin_text_list)):
        last = i == (len(bin_text_list) - 1)

        start = i * 3
        match algorithm:
            case "LSB steg":
                lsb_based.modify_pixel(pixels[start: start + 3], bin_text_list[i], last)
            case _:
                lsb_based.modify_pixel(pixels[start: start + 3], bin_text_list[i], last)

    return Image.fromarray(pixels.reshape(shape))


def encode_and_save(img_path: str, save_directory: str, save_name: str, message: str, algorithm: str, position: str):
    image_copy = Image.open(img_path, 'r').copy()

    new_img = encode_image(image_copy, message, algorithm, position)

    new_img.save(f"{save_directory}/{save_name}", 'PNG')


def decode_image(img_path: str, algorithm: str, position: str):
    image = Image.open(img_path, 'r')

    pixels, _ = image_array_reshape(image)

    data = []
    i = 0
    while True:
        start = i * 3

        if get_bin_text(data, pixels[start: start + 3], algorithm, position):
            break

        i += 1

    return decode_message(data)


class Window(QMainWindow):
    # Gui window
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 100, 1000, 800)
        self.setWindowTitle("Easy Steganography")
        self.show()
        # Encryption datas
        self.text_to_hide_label = ''
        self.encryption_image = ''
        self.encryption_output_path = ''
        # Decryption datas
        self.hiding_text = ''
        self.decryption_image = ''

        # Main control block
        main_layout = QVBoxLayout()

        ########################
        # Encryption area here #
        ########################
        encrypt_groupbox = QGroupBox("Encrypt")
        # -- Image info
        self.upload_image_button_encrypt = QPushButton("Upload Image", encrypt_groupbox)
        self.upload_image_button_encrypt.setGeometry(10, 25, 955, 200)
        self.upload_image_button_encrypt.clicked.connect(self.upload_image_encrypt)
        self.text_to_hide_label = QLabel("Messages to Hide :", encrypt_groupbox)
        self.text_to_hide_label.setGeometry(20, 250, 130, 30)
        self.text_to_hide_encrypt = QLineEdit(encrypt_groupbox)
        self.text_to_hide_encrypt.setGeometry(150, 250, 200, 30)
        # -- Encryption positions
        encryption_position_label = QLabel("Encryption Position :", encrypt_groupbox)
        encryption_position_label.setGeometry(20, 290, 140, 30)
        # ---- Encryption position buttons
        self.encryption_position_button_group = QButtonGroup(encrypt_groupbox)
        self.encryption_position_button_group.setExclusive(True)
        self.encryption_position1_btn = QRadioButton("Start", encrypt_groupbox)
        self.encryption_position2_btn = QRadioButton("End", encrypt_groupbox)
        self.encryption_position_button_group.addButton(self.encryption_position1_btn)
        self.encryption_position_button_group.addButton(self.encryption_position2_btn)
        self.encryption_position1_btn.setGeometry(150, 290, 100, 30)
        self.encryption_position2_btn.setGeometry(220, 290, 100, 30)
        self.encryption_position1_btn.setChecked(True)
        # -- Encryption methods
        encryption_method_label = QLabel("Encryption Method :", encrypt_groupbox)
        encryption_method_label.setGeometry(20, 330, 130, 30)
        # ---- Encryption algorithm buttons
        self.encryption_algorithm_button_group = QButtonGroup(encrypt_groupbox)
        self.encryption_algorithm_button_group.setExclusive(True)
        self.encryption_algorithm1_btn = QRadioButton("LSB steg", encrypt_groupbox)
        self.encryption_algorithm2_btn = QRadioButton("--", encrypt_groupbox)
        self.encryption_algorithm3_btn = QRadioButton("--", encrypt_groupbox)
        self.encryption_algorithm4_btn = QRadioButton("--", encrypt_groupbox)
        self.encryption_algorithm5_btn = QRadioButton("--", encrypt_groupbox)
        self.encryption_algorithm6_btn = QRadioButton("--", encrypt_groupbox)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm1_btn)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm2_btn)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm3_btn)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm4_btn)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm5_btn)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm6_btn)
        self.encryption_algorithm1_btn.setGeometry(150, 330, 100, 30)
        self.encryption_algorithm2_btn.setGeometry(250, 330, 100, 30)
        self.encryption_algorithm3_btn.setGeometry(350, 330, 100, 30)
        self.encryption_algorithm4_btn.setGeometry(150, 350, 100, 30)
        self.encryption_algorithm5_btn.setGeometry(250, 350, 100, 30)
        self.encryption_algorithm6_btn.setGeometry(350, 350, 100, 30)
        self.encryption_algorithm1_btn.setChecked(True)
        # ---- Encryption pass phrase
        self.encryption_pass_phrase_label = QCheckBox(" Use pass phrase :", encrypt_groupbox)
        self.encryption_pass_phrase_label.setGeometry(470, 250, 170, 30)
        self.encryption_pass_phrase = QLineEdit(encrypt_groupbox)
        self.encryption_pass_phrase.setGeometry(610, 250, 170, 30)
        # -- Output file directory
        use_pass_phrase_label = QLabel(" Select output path :", encrypt_groupbox)
        use_pass_phrase_label.setGeometry(470, 290, 170, 30)
        self.btn_select_path = QPushButton("--", encrypt_groupbox)
        self.btn_select_path.setGeometry(600, 290, 190, 30)
        self.btn_select_path.clicked.connect(self.select_path)
        self.btn_select_path.setStyleSheet("text-align: left;")
        # -- Output file name
        encryption_output_file_name_label = QLabel(" Output file name :", encrypt_groupbox)
        encryption_output_file_name_label.setGeometry(470, 330, 130, 30)
        self.encryption_output_file_name = QLineEdit(encrypt_groupbox)
        self.encryption_output_file_name.setGeometry(600, 330, 180, 30)
        # -- Process buttons
        self.encryption_alert_label = QLabel("Idling", encrypt_groupbox)
        self.encryption_alert_label.setAlignment(Qt.AlignCenter)
        self.encryption_alert_label.setGeometry(830, 250, 120, 30)
        self.encryption_process_image_btn = QPushButton("Process", encrypt_groupbox)
        self.encryption_process_image_btn.setGeometry(830, 300, 120, 30)
        self.encryption_process_image_btn.clicked.connect(self.process_encrypt)
        self.encryption_clear_btn = QPushButton("Clear", encrypt_groupbox)
        self.encryption_clear_btn.setGeometry(830, 330, 120, 30)
        self.encryption_clear_btn.clicked.connect(self.clear_encryption_area)

        ########################
        # Decryption area here #
        ########################
        decrypt_groupbox = QGroupBox("Decrypt")
        # -- Image info
        self.upload_image_button_decrypt = QPushButton("Upload Image", decrypt_groupbox)
        self.upload_image_button_decrypt.setGeometry(10, 25, 955, 200)
        self.upload_image_button_decrypt.clicked.connect(self.upload_image_decrypt)
        # -- Decryption positions
        encryption_position_label = QLabel("Decryption Position :", decrypt_groupbox)
        encryption_position_label.setGeometry(20, 250, 140, 30)
        # ---- Decryption position buttons
        self.decryption_position_button_group = QButtonGroup(decrypt_groupbox)
        self.decryption_position_button_group.setExclusive(True)
        self.decryption_position1_btn = QRadioButton("Start", decrypt_groupbox)
        self.decryption_position2_btn = QRadioButton("End", decrypt_groupbox)
        self.decryption_position_button_group.addButton(self.decryption_position1_btn)
        self.decryption_position_button_group.addButton(self.decryption_position2_btn)
        self.decryption_position1_btn.setGeometry(150, 250, 100, 30)
        self.decryption_position2_btn.setGeometry(220, 250, 100, 30)
        self.decryption_position1_btn.setChecked(True)
        # -- Decryption methods
        decryption_method_label = QLabel("Decryption Method :", decrypt_groupbox)
        decryption_method_label.setGeometry(20, 280, 130, 30)
        # ---- Decryption algorithm buttons
        self.decryption_algorithm_button_group = QButtonGroup(decrypt_groupbox)
        self.decryption_algorithm_button_group.setExclusive(True)
        self.decryption_algorithm1_btn = QRadioButton("LSB steg", decrypt_groupbox)
        self.decryption_algorithm2_btn = QRadioButton("--", decrypt_groupbox)
        self.decryption_algorithm3_btn = QRadioButton("--", decrypt_groupbox)
        self.decryption_algorithm4_btn = QRadioButton("--", decrypt_groupbox)
        self.decryption_algorithm5_btn = QRadioButton("--", decrypt_groupbox)
        self.decryption_algorithm6_btn = QRadioButton("--", decrypt_groupbox)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm1_btn)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm2_btn)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm3_btn)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm4_btn)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm5_btn)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm6_btn)
        self.decryption_algorithm1_btn.setGeometry(150, 290, 100, 30)
        self.decryption_algorithm2_btn.setGeometry(250, 290, 100, 30)
        self.decryption_algorithm3_btn.setGeometry(350, 290, 100, 30)
        self.decryption_algorithm4_btn.setGeometry(150, 310, 100, 30)
        self.decryption_algorithm5_btn.setGeometry(250, 310, 100, 30)
        self.decryption_algorithm6_btn.setGeometry(350, 310, 100, 30)
        self.decryption_algorithm1_btn.setChecked(True)
        # ---- Decryption pass phrase
        self.decryption_pass_phrase_label = QCheckBox(" Use pass phrase :", decrypt_groupbox)
        self.decryption_pass_phrase_label.setGeometry(470, 250, 170, 30)
        self.decryption_pass_phrase = QLineEdit(decrypt_groupbox)
        self.decryption_pass_phrase.setGeometry(610, 250, 170, 30)
        # -- Process buttons
        self.decryption_alert_label = QLabel("Idling", decrypt_groupbox)
        self.decryption_alert_label.setAlignment(Qt.AlignCenter)
        self.decryption_alert_label.setGeometry(475, 300, 300, 30)
        self.decryption_process_image_btn = QPushButton("Process", decrypt_groupbox)
        self.decryption_process_image_btn.setGeometry(830, 270, 120, 30)
        self.decryption_process_image_btn.clicked.connect(self.process_decrypt)
        self.decryption_clear_btn = QPushButton("Clear", decrypt_groupbox)
        self.decryption_clear_btn.setGeometry(830, 300, 120, 30)
        self.decryption_clear_btn.clicked.connect(self.clear_decryption_area)
        # ---- Decryption result messages
        self.hiding_text_label = QLabel("Messages hiding in image :", decrypt_groupbox)
        self.hiding_text_label.setGeometry(20, 350, 180, 30)
        self.hiding_text_decrypt = QLineEdit(decrypt_groupbox)
        self.hiding_text_decrypt.setGeometry(190, 350, 770, 30)
        self.hiding_text_decrypt.setReadOnly(True)

        # Adding blocks to control block
        main_layout.addWidget(encrypt_groupbox)
        main_layout.addWidget(decrypt_groupbox)
        # Widget settings
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def on_checkbox_state_changed(self, state):
        if state == 2:  # Qt.Checked
            self.text_input.setEnabled(True)  # 勾選時啟用文字輸入框
        else:
            self.text_input.setEnabled(False)

    def select_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontResolveSymlinks
        options |= QFileDialog.ShowDirsOnly

        path = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        if path:
            self.encryption_output_path = path
            self.btn_select_path.setText(self.encryption_output_path)
            self.btn_select_path.update()

    def upload_image_encrypt(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.encryption_image = file_path
            self.upload_image_button_encrypt.setStyleSheet(
                f"QPushButton {{ border-image: url('{file_path}'); border-image-outset: 30%;"
                f" background-position: center;}}")

    def upload_image_decrypt(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.decryption_image = file_path
            self.upload_image_button_decrypt.setStyleSheet(
                f"QPushButton {{ border-image: url('{file_path}'); border-image-outset: 30%;"
                f" background-position: center;}}")

    def clear_encryption_area(self):
        self.text_to_hide_encrypt.clear()
        self.encryption_image = ''
        self.upload_image_button_encrypt.setStyleSheet(
            "QPushButton { background-image: none; }"
        )
        self.encryption_position1_btn.setChecked(True)
        self.encryption_algorithm1_btn.setChecked(True)
        self.encryption_pass_phrase_label.setChecked(False)
        self.encryption_pass_phrase.clear()
        self.encryption_output_path = '--'
        self.btn_select_path.setText(self.encryption_output_path)
        self.btn_select_path.update()
        self.encryption_output_file_name.clear()

    def clear_decryption_area(self):
        self.hiding_text_decrypt.clear()
        self.decryption_image = ''
        self.upload_image_button_decrypt.setStyleSheet(
            "QPushButton { background-image: none; }"
        )
        self.decryption_position1_btn.setChecked(True)
        self.decryption_algorithm1_btn.setChecked(True)
        self.decryption_pass_phrase_label.setChecked(False)
        self.decryption_pass_phrase.clear()

    def process_encrypt(self):
        algorithm = self.encryption_algorithm_button_group.checkedButton().text()
        position = self.encryption_position_button_group.checkedButton().text()
        encode_and_save(
            self.encryption_image,
            self.encryption_output_path,
            self.encryption_output_file_name.text(),
            self.text_to_hide_encrypt.text(),
            algorithm,
            position
        )

    def process_decrypt(self):
        self.hiding_text_decrypt.clear()
        algorithm = self.decryption_algorithm_button_group.checkedButton().text()
        position = self.decryption_position_button_group.checkedButton().text()
        decryption_messages = decode_image(
            self.decryption_image,
            algorithm,
            position
        )
        print("Hiding messages:", decryption_messages)
        self.hiding_text_decrypt.setText(decryption_messages)
        self.hiding_text_decrypt.update()
