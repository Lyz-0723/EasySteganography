from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow
from PIL import Image
import numpy as np
from utils import encode_message, decode_message, image_array_reshape, text_fits_in_image
import getpass
from gpg import GPG

from Algorithms import lsb_based

basic_style = "font-weight: bold;"
gpg_path = '/Users/' + getpass.getuser() + '/.gnupg/'


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
        self.setGeometry(200, 0, 1000, 800)
        self.setWindowTitle("Easy Steganography")
        self.show()
        self.mode = 1  # 1 for encrypt, 0 for decrypt
        # Encryption datas
        self.text_to_hide_label = ''
        self.encryption_image = ''
        self.encryption_output_path = ''
        # Decryption datas
        self.hiding_text = ''
        self.decryption_image = ''
        self.encryption_key = ''
        self.decryption_key = ''

        # Main control block
        main_layout = QVBoxLayout()

        ########################
        #        NavBar        #
        ########################
        navbar_groupbox = QGroupBox("NavBar")
        navbar_groupbox.setFixedSize(1000, 60)
        self.encrypt_mode_button = QPushButton("Encrypt", navbar_groupbox)
        self.encrypt_mode_button.setGeometry(10, 20, 90, 40)
        self.encrypt_mode_button.clicked.connect(self.switch_mode)
        self.encrypt_mode_button.setEnabled(False)
        self.decrypt_mode_button = QPushButton("Decrypt", navbar_groupbox)
        self.decrypt_mode_button.setGeometry(90, 20, 90, 40)
        self.decrypt_mode_button.clicked.connect(self.switch_mode)
        self.decrypt_mode_button.setEnabled(True)
        gpg_setting_button = QPushButton("GPG setting", navbar_groupbox)
        gpg_setting_button.setGeometry(680, 20, 110, 40)
        gpg_setting_button.clicked.connect(self.open_gpg_setting)
        key_generator_button = QPushButton("Key generator", navbar_groupbox)
        key_generator_button.setGeometry(785, 20, 120, 40)
        key_generator_button.clicked.connect(self.open_key_generator)
        directions_button = QPushButton("Directions", navbar_groupbox)
        directions_button.setGeometry(900, 20, 100, 40)

        ########################
        # Encryption area here #
        ########################
        self.encrypt_groupbox = QGroupBox("Encrypt")
        # -- Image info
        self.upload_image_button_encrypt = QPushButton("Upload Image", self.encrypt_groupbox)
        self.upload_image_button_encrypt.setGeometry(10, 25, 980, 400)
        self.upload_image_button_encrypt.clicked.connect(self.upload_image_encrypt)
        self.text_to_hide_label = QLabel("Messages to hide :", self.encrypt_groupbox)
        self.text_to_hide_label.setGeometry(20, 430, 130, 30)
        self.text_to_hide_encrypt = QTextEdit(self.encrypt_groupbox)
        self.text_to_hide_encrypt.setGeometry(20, 460, 650, 105)
        # -- Encryption positions
        encryption_position_label = QLabel("Encryption Position :", self.encrypt_groupbox)
        encryption_position_label.setGeometry(20, 580, 140, 30)
        # ---- Encryption position buttons
        self.encrypt_gpg_key = QPushButton("Upload Encryption Key", self.encrypt_groupbox)
        self.encrypt_gpg_key.setGeometry(685, 457, 304, 110)
        self.encrypt_gpg_key.clicked.connect(self.upload_encryption_key)
        self.encryption_position_button_group = QButtonGroup(self.encrypt_groupbox)
        self.encryption_position_button_group.setExclusive(True)
        self.encryption_position1_btn = QRadioButton("Start", self.encrypt_groupbox)
        self.encryption_position2_btn = QRadioButton("End", self.encrypt_groupbox)
        self.encryption_position_button_group.addButton(self.encryption_position1_btn)
        self.encryption_position_button_group.addButton(self.encryption_position2_btn)
        self.encryption_position1_btn.setGeometry(150, 580, 100, 30)
        self.encryption_position2_btn.setGeometry(220, 580, 100, 30)
        self.encryption_position1_btn.setChecked(True)
        # -- Encryption methods
        encryption_method_label = QLabel("Encryption Method :", self.encrypt_groupbox)
        encryption_method_label.setGeometry(20, 620, 130, 30)
        # ---- Encryption algorithm buttons
        self.encryption_algorithm_button_group = QButtonGroup(self.encrypt_groupbox)
        self.encryption_algorithm_button_group.setExclusive(True)
        self.encryption_algorithm1_btn = QRadioButton("LSB steg", self.encrypt_groupbox)
        self.encryption_algorithm2_btn = QRadioButton("--", self.encrypt_groupbox)
        self.encryption_algorithm3_btn = QRadioButton("--", self.encrypt_groupbox)
        self.encryption_algorithm4_btn = QRadioButton("--", self.encrypt_groupbox)
        self.encryption_algorithm5_btn = QRadioButton("--", self.encrypt_groupbox)
        self.encryption_algorithm6_btn = QRadioButton("--", self.encrypt_groupbox)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm1_btn)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm2_btn)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm3_btn)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm4_btn)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm5_btn)
        self.encryption_algorithm_button_group.addButton(self.encryption_algorithm6_btn)
        self.encryption_algorithm1_btn.setGeometry(150, 620, 100, 30)
        self.encryption_algorithm2_btn.setGeometry(250, 620, 100, 30)
        self.encryption_algorithm3_btn.setGeometry(350, 620, 100, 30)
        self.encryption_algorithm4_btn.setGeometry(150, 640, 100, 30)
        self.encryption_algorithm5_btn.setGeometry(250, 640, 100, 30)
        self.encryption_algorithm6_btn.setGeometry(350, 640, 100, 30)
        self.encryption_algorithm1_btn.setChecked(True)
        # -- Output file directory
        use_pass_phrase_label = QLabel("Select output path :", self.encrypt_groupbox)
        use_pass_phrase_label.setGeometry(20, 670, 170, 30)
        self.btn_select_path = QPushButton("--", self.encrypt_groupbox)
        self.btn_select_path.setGeometry(140, 670, 190, 30)
        self.btn_select_path.clicked.connect(self.select_path)
        self.btn_select_path.setStyleSheet("text-align: left;")
        # -- Output file name
        encryption_output_file_name_label = QLabel(" Output file name :", self.encrypt_groupbox)
        encryption_output_file_name_label.setGeometry(470, 620, 115, 30)
        self.encryption_output_file_name = QTextEdit(self.encrypt_groupbox)
        self.encryption_output_file_name.setGeometry(590, 623, 150, 26)
        self.encryption_output_file_name.setPlaceholderText("output")
        encryption_output_file_extension_label = QLabel(".png", self.encrypt_groupbox)
        encryption_output_file_extension_label.setGeometry(745, 620, 50, 30)
        # ---- Encryption PGP
        self.encryption_use_gpg_label = QCheckBox(" Use PGP key file", self.encrypt_groupbox)
        self.encryption_use_gpg_label.setGeometry(470, 580, 220, 30)
        # -- Process buttons
        self.encryption_alert_label = QLabel("Status : Idling", self.encrypt_groupbox)
        self.encryption_alert_label.setStyleSheet("color: white;" + basic_style)
        self.encryption_alert_label.setAlignment(Qt.AlignCenter)
        self.encryption_alert_label.setGeometry(470, 670, 400, 30)
        self.encryption_process_image_btn = QPushButton("Process", self.encrypt_groupbox)
        self.encryption_process_image_btn.setGeometry(850, 640, 120, 30)
        self.encryption_process_image_btn.clicked.connect(self.process_encrypt)
        self.encryption_clear_btn = QPushButton("Clear", self.encrypt_groupbox)
        self.encryption_clear_btn.setGeometry(850, 670, 120, 30)
        self.encryption_clear_btn.clicked.connect(self.clear_encryption_area)

        ########################
        # Decryption area here #
        ########################
        self.decrypt_groupbox = QGroupBox("Decrypt")
        # -- Image info
        self.upload_image_button_decrypt = QPushButton("Upload Image", self.decrypt_groupbox)
        self.upload_image_button_decrypt.setGeometry(10, 25, 980, 400)
        self.upload_image_button_decrypt.clicked.connect(self.upload_image_decrypt)
        # -- Decryption result messages
        self.hiding_text_label = QLabel("Messages hiding in image :", self.decrypt_groupbox)
        self.hiding_text_label.setGeometry(20, 430, 180, 30)
        self.hiding_text_decrypt = QTextEdit(self.decrypt_groupbox)
        self.hiding_text_decrypt.setGeometry(20, 460, 650, 105)
        self.hiding_text_decrypt.setReadOnly(True)
        # -- Decryption positions
        encryption_position_label = QLabel("Decryption Position :", self.decrypt_groupbox)
        encryption_position_label.setGeometry(20, 580, 140, 30)
        # ---- Decryption position buttons
        self.decrypt_gpg_key = QPushButton("Upload Decryption Key", self.decrypt_groupbox)
        self.decrypt_gpg_key.setGeometry(685, 457, 304, 110)
        self.decrypt_gpg_key.clicked.connect(self.upload_decryption_key)
        self.decryption_position_button_group = QButtonGroup(self.decrypt_groupbox)
        self.decryption_position_button_group.setExclusive(True)
        self.decryption_position1_btn = QRadioButton("Start", self.decrypt_groupbox)
        self.decryption_position2_btn = QRadioButton("End", self.decrypt_groupbox)
        self.decryption_position_button_group.addButton(self.decryption_position1_btn)
        self.decryption_position_button_group.addButton(self.decryption_position2_btn)
        self.decryption_position1_btn.setGeometry(150, 580, 100, 30)
        self.decryption_position2_btn.setGeometry(220, 580, 100, 30)
        self.decryption_position1_btn.setChecked(True)
        # -- Decryption methods
        decryption_method_label = QLabel("Decryption Method :", self.decrypt_groupbox)
        decryption_method_label.setGeometry(20, 620, 130, 30)
        # ---- Decryption algorithm buttons
        self.decryption_algorithm_button_group = QButtonGroup(self.decrypt_groupbox)
        self.decryption_algorithm_button_group.setExclusive(True)
        self.decryption_algorithm1_btn = QRadioButton("LSB steg", self.decrypt_groupbox)
        self.decryption_algorithm2_btn = QRadioButton("--", self.decrypt_groupbox)
        self.decryption_algorithm3_btn = QRadioButton("--", self.decrypt_groupbox)
        self.decryption_algorithm4_btn = QRadioButton("--", self.decrypt_groupbox)
        self.decryption_algorithm5_btn = QRadioButton("--", self.decrypt_groupbox)
        self.decryption_algorithm6_btn = QRadioButton("--", self.decrypt_groupbox)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm1_btn)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm2_btn)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm3_btn)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm4_btn)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm5_btn)
        self.decryption_algorithm_button_group.addButton(self.decryption_algorithm6_btn)
        self.decryption_algorithm1_btn.setGeometry(150, 620, 100, 30)
        self.decryption_algorithm2_btn.setGeometry(250, 620, 100, 30)
        self.decryption_algorithm3_btn.setGeometry(350, 620, 100, 30)
        self.decryption_algorithm4_btn.setGeometry(150, 640, 100, 30)
        self.decryption_algorithm5_btn.setGeometry(250, 640, 100, 30)
        self.decryption_algorithm6_btn.setGeometry(350, 640, 100, 30)
        self.decryption_algorithm1_btn.setChecked(True)
        # ---- Decryption PGP
        self.decryption_gpg_key_label = QCheckBox(" Use PGP (Enter pass phrase) :", self.decrypt_groupbox)
        self.decryption_gpg_key_label.setGeometry(20, 670, 220, 30)
        self.decryption_gpg_key_pass_phrase = QTextEdit(self.decrypt_groupbox)
        self.decryption_gpg_key_pass_phrase.setGeometry(235, 673, 250, 26)
        # -- Process buttons
        self.decryption_alert_label = QLabel("Status : Idling", self.decrypt_groupbox)
        self.decryption_alert_label.setStyleSheet("color: white; " + basic_style)
        self.decryption_alert_label.setAlignment(Qt.AlignCenter)
        self.decryption_alert_label.setGeometry(470, 670, 400, 30)
        self.decryption_process_image_btn = QPushButton("Process", self.decrypt_groupbox)
        self.decryption_process_image_btn.setGeometry(850, 640, 120, 30)
        self.decryption_process_image_btn.clicked.connect(self.process_decrypt)
        self.decryption_clear_btn = QPushButton("Clear", self.decrypt_groupbox)
        self.decryption_clear_btn.setGeometry(850, 670, 120, 30)
        self.decryption_clear_btn.clicked.connect(self.clear_decryption_area)

        # Adding blocks to control block
        main_layout.addWidget(navbar_groupbox)
        main_layout.addWidget(self.encrypt_groupbox)
        main_layout.addWidget(self.decrypt_groupbox)
        self.encrypt_groupbox.setVisible(True)
        self.decrypt_groupbox.setVisible(False)
        # Widget settings
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def switch_mode(self):
        if self.mode == 0:
            self.encrypt_mode_button.setEnabled(False)
            self.decrypt_mode_button.setEnabled(True)
            self.encrypt_groupbox.setVisible(True)
            self.decrypt_groupbox.setVisible(False)
            self.mode = 1
        else:
            self.encrypt_mode_button.setEnabled(True)
            self.decrypt_mode_button.setEnabled(False)
            self.encrypt_groupbox.setVisible(False)
            self.decrypt_groupbox.setVisible(True)
            self.mode = 0

    def open_key_generator(self):
        dialog = KeyGenerator(self)
        dialog.exec_()

    def open_gpg_setting(self):
        dialog = GPGSetting(self)
        dialog.exec_()

    def on_checkbox_state_changed(self, state):
        if state == 2:
            self.text_input.setEnabled(True)
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
            self.upload_image_button_encrypt.setText("")

    def upload_image_decrypt(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.decryption_image = file_path
            self.upload_image_button_decrypt.setStyleSheet(
                f"QPushButton {{ border-image: url('{file_path}'); border-image-outset: 30%;"
                f" background-position: center;}}")
            self.upload_image_button_decrypt.setText('')

    def upload_encryption_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Encryption Key File", "", "Image Files (*.asc)")
        if file_path:
            self.encryption_key = file_path
            file_name = (file_path.split('/')[-1]).split('_')
            self.encrypt_gpg_key.setText(file_name[0][:7] + '...' + file_name[-2] + '_' + file_name[-1])
            self.encrypt_gpg_key.setStyleSheet('color: yellow;')

    def upload_decryption_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Decryption Key File", "", "Image Files (*.asc)")
        if file_path:
            self.decryption_key = file_path
            file_name = (file_path.split('/')[-1]).split('_')
            self.decrypt_gpg_key.setText(file_name[0][:7] + '...' + file_name[-2] + '_' + file_name[-1])
            self.decrypt_gpg_key.setStyleSheet('color: yellow;')

    def clear_encryption_area(self):
        self.encryption_alert_label.setText('Status : Idling')
        self.upload_image_button_encrypt.setText('Upload image')
        self.encryption_alert_label.setStyleSheet("color: white;" + basic_style)
        self.text_to_hide_encrypt.clear()
        self.encryption_image = ''
        self.upload_image_button_encrypt.setStyleSheet(
            "QPushButton { background-image: none; }"
        )
        self.encryption_position1_btn.setChecked(True)
        self.encryption_algorithm1_btn.setChecked(True)
        self.encryption_output_path = '--'
        self.btn_select_path.setText(self.encryption_output_path)
        self.btn_select_path.update()
        self.encryption_output_file_name.setText('')
        self.encryption_key = ''
        self.encrypt_gpg_key.setText('Upload Encryption Key')
        self.encrypt_gpg_key.setStyleSheet('color: white;')

    def clear_decryption_area(self):
        self.decryption_alert_label.setText('Status : Idling')
        self.upload_image_button_decrypt.setText('Upload image')
        self.encryption_alert_label.setStyleSheet("color: white;" + basic_style)
        self.hiding_text_decrypt.clear()
        self.decryption_image = ''
        self.upload_image_button_decrypt.setStyleSheet(
            "QPushButton { background-image: none; }"
        )
        self.decryption_position1_btn.setChecked(True)
        self.decryption_algorithm1_btn.setChecked(True)
        self.decryption_gpg_key_label.setChecked(False)
        self.decryption_gpg_key_pass_phrase.clear()
        self.decryption_key = ''
        self.decrypt_gpg_key.setText('Upload Decryption Key')
        self.decrypt_gpg_key.setStyleSheet('color: white;')

    def process_encrypt(self):

        image = self.encryption_image
        algorithm = self.encryption_algorithm_button_group.checkedButton().text()
        position = self.encryption_position_button_group.checkedButton().text()
        path = self.encryption_output_path
        output_file_name = self.encryption_output_file_name.toPlainText().split('.')[0] + '.png'
        text = self.text_to_hide_encrypt.toPlainText()
        gpg = GPG(gpg_path)

        if output_file_name == '.png':
            output_file_name = 'output.png'
        if self.encryption_use_gpg_label.checkState():
            if self.encryption_key == '':
                self.encryption_alert_label.setText('Status : Failed, no key file selected')
                self.encryption_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
                return
            try:
                text = gpg.encrypt_message(text, self.encryption_key)
            except:
                self.encryption_alert_label.setText('Status : Failed, encryption error')
                self.encryption_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
                return
        if image == '':
            self.encryption_alert_label.setText('Status : Failed, no image selected')
            self.encryption_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
            return
        if path == '':
            self.encryption_alert_label.setText('Status : Failed, no output path selected')
            self.encryption_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
            return
        encode_and_save(
            image,
            path,
            output_file_name,
            text,
            algorithm,
            position
        )
        self.encryption_alert_label.setText('Status : Done')
        self.encryption_alert_label.setStyleSheet("color: #98FB98;" + basic_style)

    def process_decrypt(self):
        self.hiding_text_decrypt.clear()
        algorithm = self.decryption_algorithm_button_group.checkedButton().text()
        position = self.decryption_position_button_group.checkedButton().text()
        key = self.decrypt_gpg_key.text()
        image = self.decryption_image
        pass_phrase = ''
        gpg = GPG(gpg_path)

        if self.decryption_gpg_key_label.checkState():
            pass_phrase = self.decryption_gpg_key_pass_phrase.toPlainText()
            if pass_phrase == '':
                self.decryption_alert_label.setText('Status : Failed, no pass phrase provided')
                self.decryption_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
                return
            if self.decryption_key == '':
                self.decryption_alert_label.setText('Status : Failed, no decryption key selected')
                self.decryption_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
                return
        if image == '':
            self.decryption_alert_label.setText('Status : Failed, no image selected')
            self.decryption_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
            return
        decryption_messages = decode_image(
            image,
            algorithm,
            position
        )
        if self.decryption_gpg_key_label.checkState():
            try:
                decryption_messages = gpg.decrypt_message(decryption_messages, self.decryption_key, pass_phrase)
            except:
                self.decryption_alert_label.setText('Status : Failed, decryption error')
                self.decryption_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
                return
        print("Hiding messages:", decryption_messages)
        self.decryption_alert_label.setText('Status : Done')
        self.decryption_alert_label.setStyleSheet("color: #98FB98;" + basic_style)
        self.hiding_text_decrypt.setText(decryption_messages)
        self.hiding_text_decrypt.update()


class GPGSetting(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GPG setting")
        self.setGeometry(0, 0, 400, 110)
        self.move(parent.geometry().x() + int(self.width() / 2), parent.geometry().y())
        global gpg_path

        # Main control block
        main_layout = QVBoxLayout()
        groupbox = QGroupBox("GPG setting")

        # Add controls to the groupbox
        self.gpg_setting_label = QLabel("Change GnuPG path for public / private key process.", groupbox)
        self.gpg_setting_label.setGeometry(10, 20, 350, 30)
        self.gpg_path_label = QLabel("GnuPG path :", groupbox)
        self.gpg_path_label.setGeometry(10, 50, 100, 30)
        self.gpg_path = QTextEdit(gpg_path, groupbox)
        self.gpg_path.setText(gpg_path)
        self.gpg_path.setGeometry(100, 53, 150, 26)
        self.gpg_path.textChanged.connect(self.on_path_change)
        self.gpg_path.setStyleSheet("text-align: left;")

        main_layout.addWidget(groupbox)

        # Widget settings
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setLayout(main_layout)

    def on_path_change(self):
        global gpg_path
        gpg_path = self.gpg_path.toPlainText()


class KeyGenerator(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Key generator")
        self.setGeometry(0, 0, 400, 200)
        self.move(parent.geometry().x() + int(self.width() / 2), parent.geometry().y())
        self.path = ''

        # Main control block
        main_layout = QVBoxLayout()
        groupbox = QGroupBox("Key generator")

        # Add controls to the groupbox
        self.key_generator_label = QLabel("Enter pass phrase to generate public / private key pair.", groupbox)
        self.key_generator_label.setGeometry(10, 20, 350, 30)
        self.pass_phrase_label = QLabel("Pass phrase :", groupbox)
        self.pass_phrase_label.setGeometry(10, 50, 100, 30)
        self.pass_phrase = QTextEdit(groupbox)
        self.pass_phrase.setGeometry(100, 53, 150, 26)
        self.select_output_path_label = QLabel("Key pair output path :", groupbox)
        self.select_output_path_label.setGeometry(10, 80, 150, 30)
        self.select_output_path = QPushButton("--", groupbox)
        self.select_output_path.setGeometry(140, 80, 150, 30)
        self.select_output_path.clicked.connect(self.select_path)
        self.select_output_path.setStyleSheet("text-align: left;")
        self.generate_btn = QPushButton("Generate", groupbox)
        self.generate_btn.setGeometry(240, 140, 110, 30)
        self.generate_btn.clicked.connect(self.process_generate)
        self.key_generator_alert_label = QLabel("Status : Idling", groupbox)
        self.key_generator_alert_label.setStyleSheet("color: white;" + basic_style)
        self.key_generator_alert_label.setAlignment(Qt.AlignCenter)
        self.key_generator_alert_label.setGeometry(10, 130, 240, 30)

        main_layout.addWidget(groupbox)

        # Widget settings
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setLayout(main_layout)

    def select_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontResolveSymlinks
        options |= QFileDialog.ShowDirsOnly

        path = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        if path:
            self.path = path
            self.select_output_path.setText(self.path)
            self.select_output_path.update()

    def process_generate(self):
        pass_phrase = self.pass_phrase.toPlainText()
        path = self.select_output_path.text()
        if path == '--':
            self.key_generator_alert_label.setText('Status : Error!No selected path.')
            self.key_generator_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
            return
        elif pass_phrase == '':
            self.key_generator_alert_label.setText('Status : Failed, no pass phrase')
            self.key_generator_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
            return
        gpg = GPG(gpg_path)
        try:
            gpg.generate_key_pairs(path, pass_phrase)
            self.key_generator_alert_label.setText('Status : Done')
            self.key_generator_alert_label.setStyleSheet("color: #98FB98;" + basic_style)
        except:
            self.key_generator_alert_label.setText('Status : Failed')
            self.key_generator_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
