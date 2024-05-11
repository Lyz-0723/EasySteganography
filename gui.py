from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow


def on_button_clicked(button) -> None:
    # Change the encryption / decryption algorithm
    print(f"{button.text()} selected")


class Window(QMainWindow):
    # Gui window
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 50, 1000, 800)
        self.setWindowTitle("Main window")
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
        self.encryption_position_button_group.buttonClicked.connect(on_button_clicked)
        self.encryption_position1_btn.setChecked(True)
        # -- Encryption methods
        encryption_method_label = QLabel("Encryption Method :", encrypt_groupbox)
        encryption_method_label.setGeometry(20, 330, 130, 30)
        # ---- Encryption algorithm buttons
        self.encryption_algorithm_button_group = QButtonGroup(encrypt_groupbox)
        self.encryption_algorithm_button_group.setExclusive(True)
        self.encryption_algorithm1_btn = QRadioButton("Algorithm 1", encrypt_groupbox)
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
        self.encryption_algorithm_button_group.buttonClicked.connect(on_button_clicked)
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
        # self.encryption_process_image_btn.clicked.connect()
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
        self.decryption_position_button_group.buttonClicked.connect(on_button_clicked)
        self.decryption_position1_btn.setChecked(True)
        # -- Decryption methods
        decryption_method_label = QLabel("Decryption Method :", decrypt_groupbox)
        decryption_method_label.setGeometry(20, 280, 130, 30)
        # ---- Decryption algorithm buttons
        self.decryption_algorithm_button_group = QButtonGroup(decrypt_groupbox)
        self.decryption_algorithm_button_group.setExclusive(True)
        self.decryption_algorithm1_btn = QRadioButton("Algorithm 1", decrypt_groupbox)
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
        self.decryption_algorithm_button_group.buttonClicked.connect(on_button_clicked)
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
        # self.encryption_process_image_btn.clicked.connect()
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
