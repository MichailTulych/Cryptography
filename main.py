from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from sympy import isprime, randprime
import random
import sys
import pyperclip

bits = 8
public_key = None
private_key = None


def generate_keys():
    global public_key, private_key
    public_key, private_key = generation_key(bits)


def encrypt(plaintext, public_key):
    key, n = public_key
    encrypted_values = []
    for char in plaintext:
        encrypted_value = (ord(char) ** key) % n
        encrypted_values.append(str(encrypted_value))
    return ' '.join(encrypted_values)


def decrypt(cipher_text, private_key):
    key, n = private_key
    encrypted_values = cipher_text.split()
    plain = []
    for value in encrypted_values:
        char = chr((int(value) ** key) % n)
        plain.append(char)
    return ''.join(plain)


def multiplicative_reciprocal(a, m):
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1


def NOD(number1, number2):
    while number2 != 0:
        number1, number2 = number2, number1 % number2
    return number1


def generation_key(bits):
    p = randprime(2**(bits-1), 2**bits)
    q = randprime(2**(bits-1), 2**bits)
    phi = (p - 1) * (q - 1)
    n = p * q
    e = random.randrange(2, phi)
    g = NOD(e, phi)
    while g != 1:
        e = random.randrange(2, phi)
        g = NOD(e, phi)

    d = multiplicative_reciprocal(e, phi)
    return ((e, n), (d, n))


class KeyGenerationThread(QThread):
    finished = pyqtSignal()
    def run(self):
        generate_keys()
        self.finished.emit()

class MainWindow(QWidget):
    def generate_keys(self):
        self.thread = KeyGenerationThread()
        self.thread.finished.connect(self.keys_generated)
        self.thread.start()

    def keys_generated(self):
        QMessageBox.information(self, "Ключи сгенерированы", "Ключи успешно сгенерированы!")

    def launch_encrypt(self):
        try:
            plaintext = self.text_entry.text()
            if not plaintext:
                raise ValueError("Введите сообщение для шифрования.")
            if not public_key:
                raise ValueError("Сначала сгенерируйте ключи.")
            cipher_text = encrypt(plaintext, public_key)
            self.result_text.setPlainText(cipher_text)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def launch_decrypt(self):
        try:
            cipher_text = self.text_entry.text()
            if not cipher_text:
                raise ValueError("Введите зашифрованное сообщение для расшифровки.")
            if not private_key:
                raise ValueError("Сначала сгенерируйте ключи.")
            plaintext = decrypt(cipher_text, private_key)
            self.result_text.setPlainText(plaintext)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def copy_to_clipboard(self):
        pyperclip.copy(self.result_text.toPlainText())
        QMessageBox.information(self, "Скопировано", "Результат скопирован в буфер обмена.")

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("RSA digital signature")

        layout = QVBoxLayout()

        self.text_label = QLabel("Введите сообщение:")
        layout.addWidget(self.text_label)

        self.text_entry = QLineEdit()
        layout.addWidget(self.text_entry)

        button_layout = QHBoxLayout()

        self.generate_button = QPushButton("Сгенерировать ключи")
        self.generate_button.clicked.connect(self.generate_keys)
        button_layout.addWidget(self.generate_button)

        self.encrypt_button = QPushButton("Зашифровать")
        self.encrypt_button.clicked.connect(self.launch_encrypt)
        button_layout.addWidget(self.encrypt_button)

        self.decrypt_button = QPushButton("Расшифровать")
        self.decrypt_button.clicked.connect(self.launch_decrypt)
        button_layout.addWidget(self.decrypt_button)

        layout.addLayout(button_layout)

        self.result_label = QLabel("Результат:")
        layout.addWidget(self.result_label)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.copy_button = QPushButton("Скопировать в буфер обмена")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(self.copy_button)

        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
