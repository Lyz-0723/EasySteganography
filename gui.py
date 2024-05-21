from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow
from PIL import Image
import numpy as np
from utils import encode_message, decode_message, image_array_reshape, text_fits_in_image
import getpass
from gpg import GPG

from Algorithms import lsb_based, pvd_based

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
    # Encode the image with corresponding algorithm
    bin_text_list = encode_message(message)
    pixels, shape = image_array_reshape(image)

    if not text_fits_in_image(pixels, message):
        print('Message is too long')
        return

    match algorithm:
        case "LSB steg":
            # LSB steg Send each three pixels for encoding data
            for i in range(len(bin_text_list)):
                last = i == (len(bin_text_list) - 1)
                start = i * 3
                lsb_based.modify_pixel(pixels[start: start + 3], bin_text_list[i], last)
        case "PVD steg":
            # PVD steg send the whole image for encoding data
            pvd_based.modify_pixel(pixels[:], ''.join(bin_text_list))
        case _:
            # Default algorithm set to LSB steg
            for i in range(len(bin_text_list)):
                last = i == (len(bin_text_list) - 1)
                start = i * 3
                lsb_based.modify_pixel(pixels[start: start + 3], bin_text_list[i], last)

    return Image.fromarray(pixels.reshape(shape))


def encode_and_save(img_path: str, save_directory: str, save_name: str, message: str, algorithm: str, position: str):
    # Copy the image data and call the encode_image function then save it
    image_copy = Image.open(img_path, 'r').copy()

    new_img = encode_image(image_copy, message, algorithm, position)
    new_img.save(f"{save_directory}/{save_name}", 'PNG')


def decode_image(img_path: str, algorithm: str, position: str):
    # Decode the image no matter it is encrypted message or not
    image = Image.open(img_path, 'r')
    pixels, _ = image_array_reshape(image)

    match algorithm:
        case "LSB steg":
            data = []
            i = 0
            while True:
                start = i * 3
                if get_bin_text(data, pixels[start: start + 3], algorithm, position):
                    break
                i += 1
            return decode_message(data)
        case "PVD steg":
            return pvd_based.get_hidden_messages(pixels)
        case _:
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
        self.encode_image = ''
        self.encode_text_to_hide_label = ''
        self.encode_image_output_path = ''
        self.encode_key_file_path = ''
        # Decryption datas
        self.hiding_text = ''
        self.decode_image = ''
        self.decode_key_file_path = ''

        # Main control block
        main_layout = QVBoxLayout()

        ########################
        #        NavBar        #
        ########################
        navbar_groupbox = QGroupBox("NavBar")
        navbar_groupbox.setFixedSize(1000, 60)
        self.encode_mode_button = QPushButton("Encode", navbar_groupbox)
        self.encode_mode_button.setGeometry(10, 20, 90, 40)
        self.encode_mode_button.clicked.connect(self.switch_mode)
        self.encode_mode_button.setEnabled(False)
        self.decode_mode_button = QPushButton("Decode", navbar_groupbox)
        self.decode_mode_button.setGeometry(90, 20, 90, 40)
        self.decode_mode_button.clicked.connect(self.switch_mode)
        self.decode_mode_button.setEnabled(True)
        gpg_setting_button = QPushButton("GPG setting", navbar_groupbox)
        gpg_setting_button.setGeometry(680, 20, 110, 40)
        gpg_setting_button.clicked.connect(self.open_gpg_setting)
        key_generator_button = QPushButton("Key generator", navbar_groupbox)
        key_generator_button.setGeometry(785, 20, 120, 40)
        key_generator_button.clicked.connect(self.open_key_generator)
        directions_button = QPushButton("Directions", navbar_groupbox)
        directions_button.setGeometry(900, 20, 100, 40)
        directions_button.clicked.connect(self.open_direction)

        ########################
        #   Encode area here   #
        ########################
        self.encode_groupbox = QGroupBox("Encrypt")
        # -- Image info
        self.encode_upload_image_btn = QPushButton("Upload Image", self.encode_groupbox)
        self.encode_upload_image_btn.setGeometry(10, 25, 980, 400)
        self.encode_upload_image_btn.clicked.connect(self.encode_upload_image)
        self.encode_text_to_hide_label = QLabel("Messages to hide :", self.encode_groupbox)
        self.encode_text_to_hide_label.setGeometry(20, 430, 130, 30)
        self.encode_text_to_hide = QTextEdit(self.encode_groupbox)
        self.encode_text_to_hide.setGeometry(20, 460, 650, 105)
        # -- Encode positions
        encode_position_label = QLabel("Encryption Position :", self.encode_groupbox)
        encode_position_label.setGeometry(20, 580, 140, 30)
        # ---- Encode position buttons
        self.encode_upload_pgp_key_btn = QPushButton("Upload encode Key", self.encode_groupbox)
        self.encode_upload_pgp_key_btn.setGeometry(685, 457, 304, 110)
        self.encode_upload_pgp_key_btn.clicked.connect(self.encode_upload_pgp_key)

        self.encode_position_btn_group = QButtonGroup(self.encode_groupbox)
        self.encode_position_btn_group.setExclusive(True)
        self.encode_position_start_btn = QRadioButton("Start", self.encode_groupbox)
        self.encode_position_end_btn = QRadioButton("End", self.encode_groupbox)
        self.encode_position_btn_group.addButton(self.encode_position_start_btn)
        self.encode_position_btn_group.addButton(self.encode_position_end_btn)
        self.encode_position_start_btn.setGeometry(150, 580, 100, 30)
        self.encode_position_end_btn.setGeometry(220, 580, 100, 30)
        self.encode_position_start_btn.setChecked(True)

        # -- Encode methods
        encode_method_label = QLabel("Encode Method :", self.encode_groupbox)
        encode_method_label.setGeometry(20, 620, 130, 30)
        # ---- Encode algorithm buttons
        self.encode_algorithm_btn_group = QButtonGroup(self.encode_groupbox)
        self.encode_algorithm_btn_group.setExclusive(True)
        self.encode_algorithm1_btn = QRadioButton("LSB steg", self.encode_groupbox)
        self.encode_algorithm2_btn = QRadioButton("PVD steg", self.encode_groupbox)
        self.encode_algorithm3_btn = QRadioButton("--", self.encode_groupbox)
        self.encode_algorithm4_btn = QRadioButton("--", self.encode_groupbox)
        self.encode_algorithm5_btn = QRadioButton("--", self.encode_groupbox)
        self.encode_algorithm6_btn = QRadioButton("--", self.encode_groupbox)
        self.encode_algorithm_btn_group.addButton(self.encode_algorithm1_btn)
        self.encode_algorithm_btn_group.addButton(self.encode_algorithm2_btn)
        self.encode_algorithm_btn_group.addButton(self.encode_algorithm3_btn)
        self.encode_algorithm_btn_group.addButton(self.encode_algorithm4_btn)
        self.encode_algorithm_btn_group.addButton(self.encode_algorithm5_btn)
        self.encode_algorithm_btn_group.addButton(self.encode_algorithm6_btn)
        self.encode_algorithm1_btn.setGeometry(150, 620, 100, 30)
        self.encode_algorithm2_btn.setGeometry(250, 620, 100, 30)
        self.encode_algorithm3_btn.setGeometry(350, 620, 100, 30)
        self.encode_algorithm4_btn.setGeometry(150, 640, 100, 30)
        self.encode_algorithm5_btn.setGeometry(250, 640, 100, 30)
        self.encode_algorithm6_btn.setGeometry(350, 640, 100, 30)
        self.encode_algorithm1_btn.setChecked(True)

        # -- Encode output file directory
        encode_use_pass_phrase_label = QLabel("Select output path :", self.encode_groupbox)
        encode_use_pass_phrase_label.setGeometry(20, 670, 170, 30)
        self.encode_output_file_path_btn = QPushButton("--", self.encode_groupbox)
        self.encode_output_file_path_btn.setGeometry(140, 670, 190, 30)
        self.encode_output_file_path_btn.clicked.connect(self.encode_select_output_file_path)
        self.encode_output_file_path_btn.setStyleSheet("text-align: left;")
        # -- Encode output file name
        encode_output_file_name_label = QLabel(" Output file name :", self.encode_groupbox)
        encode_output_file_name_label.setGeometry(470, 620, 115, 30)
        self.encode_output_file_name = QTextEdit(self.encode_groupbox)
        self.encode_output_file_name.setGeometry(590, 623, 150, 26)
        self.encode_output_file_name.setPlaceholderText("output")
        encode_output_file_extension_label = QLabel(".png", self.encode_groupbox)
        encode_output_file_extension_label.setGeometry(745, 620, 50, 30)

        # -- Encode PGP
        self.encode_use_gpg_label = QCheckBox(" Use PGP key file", self.encode_groupbox)
        self.encode_use_gpg_label.setGeometry(470, 580, 220, 30)
        # -- Encode process buttons
        self.encode_alert_label = QLabel("Status : Idling", self.encode_groupbox)
        self.encode_alert_label.setStyleSheet("color: white;" + basic_style)
        self.encode_alert_label.setAlignment(Qt.AlignCenter)
        self.encode_alert_label.setGeometry(470, 670, 400, 30)
        self.encode_process_image_btn = QPushButton("Process", self.encode_groupbox)
        self.encode_process_image_btn.setGeometry(850, 640, 120, 30)
        self.encode_process_image_btn.clicked.connect(self.process_encode)
        self.encode_clear_btn = QPushButton("Clear", self.encode_groupbox)
        self.encode_clear_btn.setGeometry(850, 670, 120, 30)
        self.encode_clear_btn.clicked.connect(self.clear_encode_area)

        ########################
        #   Decode area here   #
        ########################
        self.decode_groupbox = QGroupBox("Decode")
        # -- Image info
        self.decode_upload_image_btn = QPushButton("Upload Image", self.decode_groupbox)
        self.decode_upload_image_btn.setGeometry(10, 25, 980, 400)
        self.decode_upload_image_btn.clicked.connect(self.decode_upload_image)
        # -- Decode result messages
        self.decode_hiding_text_label = QLabel("Messages hiding in image :", self.decode_groupbox)
        self.decode_hiding_text_label.setGeometry(20, 430, 180, 30)
        self.decode_hiding_text = QTextEdit(self.decode_groupbox)
        self.decode_hiding_text.setGeometry(20, 460, 650, 105)
        self.decode_hiding_text.setReadOnly(True)

        # -- Decode positions
        decode_position_label = QLabel("Decode Position :", self.decode_groupbox)
        decode_position_label.setGeometry(20, 580, 140, 30)
        # ---- Decode position buttons
        self.decode_upload_pgp_key_btn = QPushButton("Upload Decryption Key", self.decode_groupbox)
        self.decode_upload_pgp_key_btn.setGeometry(685, 457, 304, 110)
        self.decode_upload_pgp_key_btn.clicked.connect(self.decode_upload_pgp_key)
        self.decode_position_btn_group = QButtonGroup(self.decode_groupbox)
        self.decode_position_btn_group.setExclusive(True)
        self.decode_position_start_btn = QRadioButton("Start", self.decode_groupbox)
        self.decode_position_end_btn = QRadioButton("End", self.decode_groupbox)
        self.decode_position_btn_group.addButton(self.decode_position_start_btn)
        self.decode_position_btn_group.addButton(self.decode_position_end_btn)
        self.decode_position_start_btn.setGeometry(150, 580, 100, 30)
        self.decode_position_end_btn.setGeometry(220, 580, 100, 30)
        self.decode_position_start_btn.setChecked(True)

        # -- Decode methods
        decode_method_label = QLabel("Decode Method :", self.decode_groupbox)
        decode_method_label.setGeometry(20, 620, 130, 30)
        # ---- Decode algorithm buttons
        self.decode_algorithm_btn_group = QButtonGroup(self.decode_groupbox)
        self.decode_algorithm_btn_group.setExclusive(True)
        self.decode_algorithm1_btn = QRadioButton("LSB steg", self.decode_groupbox)
        self.decode_algorithm2_btn = QRadioButton("PVD steg", self.decode_groupbox)
        self.decode_algorithm3_btn = QRadioButton("--", self.decode_groupbox)
        self.decode_algorithm4_btn = QRadioButton("--", self.decode_groupbox)
        self.decode_algorithm5_btn = QRadioButton("--", self.decode_groupbox)
        self.decode_algorithm6_btn = QRadioButton("--", self.decode_groupbox)
        self.decode_algorithm_btn_group.addButton(self.decode_algorithm1_btn)
        self.decode_algorithm_btn_group.addButton(self.decode_algorithm2_btn)
        self.decode_algorithm_btn_group.addButton(self.decode_algorithm3_btn)
        self.decode_algorithm_btn_group.addButton(self.decode_algorithm4_btn)
        self.decode_algorithm_btn_group.addButton(self.decode_algorithm5_btn)
        self.decode_algorithm_btn_group.addButton(self.decode_algorithm6_btn)
        self.decode_algorithm1_btn.setGeometry(150, 620, 100, 30)
        self.decode_algorithm2_btn.setGeometry(250, 620, 100, 30)
        self.decode_algorithm3_btn.setGeometry(350, 620, 100, 30)
        self.decode_algorithm4_btn.setGeometry(150, 640, 100, 30)
        self.decode_algorithm5_btn.setGeometry(250, 640, 100, 30)
        self.decode_algorithm6_btn.setGeometry(350, 640, 100, 30)
        self.decode_algorithm1_btn.setChecked(True)

        # -- Decode PGP
        self.decode_use_pgp_key_label = QCheckBox(" Use PGP (Enter pass phrase) :", self.decode_groupbox)
        self.decode_use_pgp_key_label.setGeometry(20, 670, 220, 30)
        self.decode_pgp_key_pass_phrase = QTextEdit(self.decode_groupbox)
        self.decode_pgp_key_pass_phrase.setGeometry(235, 673, 250, 26)

        # -- Process buttons
        self.decode_alert_label = QLabel("Status : Idling", self.decode_groupbox)
        self.decode_alert_label.setStyleSheet("color: white; " + basic_style)
        self.decode_alert_label.setAlignment(Qt.AlignCenter)
        self.decode_alert_label.setGeometry(470, 670, 400, 30)
        self.decode_process_image_btn = QPushButton("Process", self.decode_groupbox)
        self.decode_process_image_btn.setGeometry(850, 640, 120, 30)
        self.decode_process_image_btn.clicked.connect(self.process_decode)
        self.decode_clear_btn = QPushButton("Clear", self.decode_groupbox)
        self.decode_clear_btn.setGeometry(850, 670, 120, 30)
        self.decode_clear_btn.clicked.connect(self.clear_decode_area)

        # Adding blocks to control block
        main_layout.addWidget(navbar_groupbox)
        main_layout.addWidget(self.encode_groupbox)
        main_layout.addWidget(self.decode_groupbox)
        self.encode_groupbox.setVisible(True)
        self.decode_groupbox.setVisible(False)

        # Widget settings
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def switch_mode(self):
        # Set encryption / decryption mode for gui
        if self.mode == 0:
            self.encode_mode_button.setEnabled(False)
            self.decode_mode_button.setEnabled(True)
            self.encode_groupbox.setVisible(True)
            self.decode_groupbox.setVisible(False)
            self.mode = 1
        else:
            self.encode_mode_button.setEnabled(True)
            self.decode_mode_button.setEnabled(False)
            self.encode_groupbox.setVisible(False)
            self.decode_groupbox.setVisible(True)
            self.mode = 0

    def open_key_generator(self):
        # Open key generator panel
        dialog = KeyGenerator(self)
        dialog.exec_()

    def open_gpg_setting(self):
        # Open gpg path setting panel
        dialog = GPGSetting(self)
        dialog.exec_()

    def open_direction(self):
        # Open tool direction panel
        dialog = Direction(self)
        dialog.exec_()

    def on_pgp_key_checkbox_state_changed(self, state):
        # Set the "Use PGP key" checkbox status
        if state == 2:
            self.text_input.setEnabled(True)
        else:
            self.text_input.setEnabled(False)

    def encode_select_output_file_path(self):
        # Select the output path for encoded image
        options = QFileDialog.Options()
        options |= QFileDialog.DontResolveSymlinks
        options |= QFileDialog.ShowDirsOnly

        path = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        if path:
            self.encode_image_output_path = path
            self.encode_output_file_path_btn.setText(self.encode_image_output_path)
            self.encode_output_file_path_btn.update()

    def encode_upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.encode_image = file_path
            self.encode_upload_image_btn.setStyleSheet(
                f"QPushButton {{ border-image: url('{file_path}');"
                f" background-position: center;}}")
            self.encode_upload_image_btn.setText("")

    def decode_upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.decode_image = file_path
            self.decode_upload_image_btn.setStyleSheet(
                f"QPushButton {{ border-image: url('{file_path}');"
                f" background-position: center;}}")
            self.decode_upload_image_btn.setText('')

    def encode_upload_pgp_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Encryption Key File", "", "Image Files (*.asc)")
        if file_path:
            self.encode_key_file_path = file_path
            file_name = (file_path.split('/')[-1]).split('_')
            self.encode_upload_pgp_key_btn.setText(file_name[0][:7] + '...' + file_name[-2] + '_' + file_name[-1])
            self.encode_upload_pgp_key_btn.setStyleSheet('color: yellow;')

    def decode_upload_pgp_key(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Decryption Key File", "", "Image Files (*.asc)")
        if file_path:
            self.decode_key_file_path = file_path
            file_name = (file_path.split('/')[-1]).split('_')
            self.decode_upload_pgp_key_btn.setText(file_name[0][:7] + '...' + file_name[-2] + '_' + file_name[-1])
            self.decode_upload_pgp_key_btn.setStyleSheet('color: yellow;')

    def clear_encode_area(self):
        self.encode_alert_label.setText('Status : Idling')
        self.encode_upload_image_btn.setText('Upload image')
        self.encode_alert_label.setStyleSheet("color: white;" + basic_style)
        self.encode_text_to_hide.clear()
        self.encode_image = ''
        self.encode_upload_image_btn.setStyleSheet(
            "QPushButton { background-image: none; }"
        )
        self.encode_position_start_btn.setChecked(True)
        self.encode_algorithm1_btn.setChecked(True)
        self.encode_image_output_path = '--'
        self.encode_output_file_path_btn.setText(self.encode_image_output_path)
        self.encode_output_file_path_btn.update()
        self.encode_output_file_name.setText('')
        self.encode_key_file_path = ''
        self.encode_upload_pgp_key_btn.setText('Upload Encryption Key')
        self.encode_upload_pgp_key_btn.setStyleSheet('color: white;')

    def clear_decode_area(self):
        self.decode_alert_label.setText('Status : Idling')
        self.decode_upload_image_btn.setText('Upload image')
        self.encode_alert_label.setStyleSheet("color: white;" + basic_style)
        self.decode_hiding_text.clear()
        self.decode_image = ''
        self.decode_upload_image_btn.setStyleSheet(
            "QPushButton { background-image: none; }"
        )
        self.decode_position_start_btn.setChecked(True)
        self.decode_algorithm1_btn.setChecked(True)
        self.decode_use_pgp_key_label.setChecked(False)
        self.decode_pgp_key_pass_phrase.clear()
        self.decode_key_file_path = ''
        self.decode_upload_pgp_key_btn.setText('Upload Decryption Key')
        self.decode_upload_pgp_key_btn.setStyleSheet('color: white;')

    def process_encode(self):
        # Process encode and encryption(if needed)
        image = self.encode_image
        algorithm = self.encode_algorithm_btn_group.checkedButton().text()
        position = self.encode_position_btn_group.checkedButton().text()
        path = self.encode_image_output_path
        output_file_name = self.encode_output_file_name.toPlainText().split('.')[0] + '.png'
        text = self.encode_text_to_hide.toPlainText()
        gpg = GPG(gpg_path)

        if output_file_name == '.png':
            output_file_name = 'output.png'
        if self.encode_use_gpg_label.checkState():
            if self.encode_key_file_path == '':
                self.encode_alert_label.setText('Status : Failed, no key file selected')
                self.encode_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
                return
            try:
                text = gpg.encrypt_message(text, self.encode_key_file_path)
            except:
                self.encode_alert_label.setText('Status : Failed, encryption error')
                self.encode_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
                return
        if image == '':
            self.encode_alert_label.setText('Status : Failed, no image selected')
            self.encode_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
            return
        if path == '':
            self.encode_alert_label.setText('Status : Failed, no output path selected')
            self.encode_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
            return
        encode_and_save(
            image,
            path,
            output_file_name,
            text,
            algorithm,
            position
        )
        self.encode_alert_label.setText('Status : Done')
        self.encode_alert_label.setStyleSheet("color: #98FB98;" + basic_style)

    def process_decode(self):
        # Process decode and decryption(if needed)
        self.decode_hiding_text.clear()
        algorithm = self.decode_algorithm_btn_group.checkedButton().text()
        position = self.decode_position_btn_group.checkedButton().text()
        key = self.decode_upload_pgp_key_btn.text()
        image = self.decode_image
        pass_phrase = ''
        gpg = GPG(gpg_path)

        if self.decode_use_pgp_key_label.checkState():
            pass_phrase = self.decode_pgp_key_pass_phrase.toPlainText()
            if pass_phrase == '':
                self.decode_alert_label.setText('Status : Failed, no pass phrase provided')
                self.decode_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
                return
            if self.decode_key_file_path == '':
                self.decode_alert_label.setText('Status : Failed, no decryption key selected')
                self.decode_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
                return
        if image == '':
            self.decode_alert_label.setText('Status : Failed, no image selected')
            self.decode_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
            return
        decryption_messages = decode_image(
            image,
            algorithm,
            position
        )
        if self.decode_use_pgp_key_label.checkState():
            try:
                decryption_messages = gpg.decrypt_message(decryption_messages, self.decode_key_file_path, pass_phrase)
            except:
                self.decode_alert_label.setText('Status : Failed, decryption error')
                self.decode_alert_label.setStyleSheet("color: #FF4500;" + basic_style)
                return
        print("Hiding messages:", decryption_messages)
        self.decode_alert_label.setText('Status : Done')
        self.decode_alert_label.setStyleSheet("color: #98FB98;" + basic_style)
        self.decode_hiding_text.setText(decryption_messages)
        self.decode_hiding_text.update()


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
        self.select_output_path.clicked.connect(self.select_key_output_path)
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

    def select_key_output_path(self):
        # Select generated key file output path
        options = QFileDialog.Options()
        options |= QFileDialog.DontResolveSymlinks
        options |= QFileDialog.ShowDirsOnly

        path = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        if path:
            self.path = path
            self.select_output_path.setText(self.path)
            self.select_output_path.update()

    def process_generate(self):
        # Generate public / private key pair
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


class Direction(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Direction")
        self.setGeometry(0, 0, 500, 670)
        self.move(parent.geometry().x() + int(self.width() / 2), parent.geometry().y())

        # Main control block
        main_layout = QVBoxLayout()
        operation_groupbox = QGroupBox("Operation")
        operation_groupbox.setFixedSize(500, 530)

        # Encryption directions
        self.subtitle_encode = QLabel("Encode:", operation_groupbox)
        self.subtitle_encode.setStyleSheet("font-size: 15px; color: orange;" + basic_style)
        self.subtitle_encode.setGeometry(10, 20, 350, 30)
        self.encode_line1 = QLabel('1. Select image, position and algorithm to encrypt.', operation_groupbox)
        self.encode_line1.setGeometry(15, 40, 500, 30)
        self.encode_line2 = QLabel('2. Enter messages you want to hide.', operation_groupbox)
        self.encode_line2.setGeometry(15, 60, 500, 30)
        self.encode_line3 = QLabel('3. If you want to protect the messages with one more layer,', operation_groupbox)
        self.encode_line3.setGeometry(15, 80, 500, 30)
        self.encode_line4 = QLabel('    upload encode key file and select "Use PGP key file".', operation_groupbox)
        self.encode_line4.setGeometry(15, 95, 500, 30)
        self.encode_line5 = QLabel('4. Select output file path and change the output file name(if you want).',
                                   operation_groupbox)
        self.encode_line5.setGeometry(15, 115, 500, 30)
        self.encode_line6 = QLabel('5. Hit "Process" to encode or "Clear" to clean the data.', operation_groupbox)
        self.encode_line6.setGeometry(15, 135, 500, 30)

        # Decryption directions
        self.subtitle_decode = QLabel("Decode:", operation_groupbox)
        self.subtitle_decode.setStyleSheet("font-size: 15px; color: orange;" + basic_style)
        self.subtitle_decode.setGeometry(10, 165, 350, 30)
        self.decode_line1 = QLabel('1. Select image, position and algorithm to decode.', operation_groupbox)
        self.decode_line1.setGeometry(15, 185, 500, 30)
        self.decode_line2 = QLabel('2. If the messages has been protected, upload decode key.', operation_groupbox)
        self.decode_line2.setGeometry(15, 205, 500, 30)
        self.decode_line3 = QLabel('    file and select "Use PGP key file", then enter pass phrase.', operation_groupbox)
        self.decode_line3.setGeometry(15, 220, 500, 30)
        self.decode_line4 = QLabel('3. Hit "Process" to decode or "Clear" to clean the data.', operation_groupbox)
        self.decode_line4.setGeometry(15, 240, 500, 30)
        self.decode_line5 = QLabel('4. You will see the original messages in the text box.', operation_groupbox)
        self.decode_line5.setGeometry(15, 260, 500, 30)
        self.decode_line6 = QLabel('-- You can also view the encrypted messages by not selecting', operation_groupbox)
        self.decode_line6.setGeometry(20, 280, 500, 30)
        self.decode_line7 = QLabel('   "Use PGP key file".', operation_groupbox)
        self.decode_line7.setGeometry(20, 300, 500, 30)

        # Key generation
        self.subtitle_key_generate = QLabel("Key Generation:", operation_groupbox)
        self.subtitle_key_generate.setStyleSheet("font-size: 15px; color: orange;" + basic_style)
        self.subtitle_key_generate.setGeometry(10, 330, 350, 30)
        self.key_generate_line1 = QLabel("This tool has provided a way to generate public / private key pair - ",
                                         operation_groupbox)
        self.key_generate_line1.setGeometry(15, 350, 500, 30)
        self.key_generate_line2 = QLabel("1. Make sure you have installed GnuPG in your computer.", operation_groupbox)
        self.key_generate_line2.setGeometry(15, 370, 500, 30)
        self.key_generate_line3 = QLabel('2. Check the GnuPG path in "GPG Setting".', operation_groupbox)
        self.key_generate_line3.setGeometry(15, 390, 500, 30)
        self.key_generate_line4 = QLabel('3. Open "Key generator" and select key output file path.', operation_groupbox)
        self.key_generate_line4.setGeometry(15, 410, 500, 30)
        self.key_generate_line5 = QLabel('4. Enter pass phrase.', operation_groupbox)
        self.key_generate_line5.setGeometry(15, 430, 500, 30)
        self.key_generate_line6 = QLabel('5. Hit "Process" to generate key pair.', operation_groupbox)
        self.key_generate_line6.setGeometry(15, 450, 500, 30)
        self.key_generate_line7 = QLabel('6. If the generation succeed, you should see a folder in the path you',
                                         operation_groupbox)
        self.key_generate_line7.setGeometry(15, 470, 500, 30)
        self.key_generate_line8 = QLabel('   select, inside are public / private key file and '
                                         'rev file for storing them.',
                                         operation_groupbox)
        self.key_generate_line8.setGeometry(15, 490, 500, 30)

        license_groupbox = QGroupBox("License")
        self.license_line1 = QLabel("Free to use for all kind of work, but please link the source if you are using it",
                                    license_groupbox)
        self.license_line1.setGeometry(10, 20, 500, 30)
        self.license_line2 = QLabel("as your code's base.", license_groupbox)
        self.license_line2.setGeometry(10, 35, 500, 30)
        self.license_line3 = QLabel("Contributed by: Danny Ho, Sally Lin.", license_groupbox)
        self.license_line3.setGeometry(10, 55, 500, 30)
        self.license_line4 = QLabel("GitHub source page: <a href='https://github.com/Lyz-0723/EasySteganography'>"
                                    "here</a>", license_groupbox)
        self.license_line4.setTextFormat(Qt.RichText)
        self.license_line4.setOpenExternalLinks(True)
        self.license_line4.setGeometry(10, 75, 500, 30)

        main_layout.addWidget(operation_groupbox)
        main_layout.addWidget(license_groupbox)
        # Widget settings
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setLayout(main_layout)
