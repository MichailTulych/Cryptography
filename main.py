import sys
import struct
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox)

WORD_SIZE = 32
ROUNDS = 12
KEY_SIZE = 16
P = 0xB7E15163
Q = 0x9E3779B9

# функция для циклического сдвига влево
def left_rotate(value, shift):
    return ((value << shift) & 0xFFFFFFFF) | (value >> (WORD_SIZE - shift))

# функция для циклического сдвига вправо
def right_rotate(value, shift):
    return ((value >> shift) | (value << (WORD_SIZE - shift))) & 0xFFFFFFFF

# Генерация расширенного ключа
def key_schedule(key):
    L = [int.from_bytes(key[i:i+4], 'little') for i in range(0, len(key), 4)]
    S = [P]
    for i in range(1, 2 * ROUNDS + 2):
        S.append((S[i - 1] + Q) & 0xFFFFFFFF)
    i = j = A = B = 0
    for k in range(3 * max(len(L), len(S))):
        A = S[i] = left_rotate((S[i] + A + B) & 0xFFFFFFFF, 3)
        B = L[j] = left_rotate(
            (L[j] + A + B) & 0xFFFFFFFF, (A + B) % WORD_SIZE)
        i = (i + 1) % len(S)
        j = (j + 1) % len(L)
    return S

# Шифрование
def encrypt(plaintext, S):
    A, B = struct.unpack('<2I', plaintext)
    A = (A + S[0]) & 0xFFFFFFFF
    B = (B + S[1]) & 0xFFFFFFFF
    for i in range(1, ROUNDS + 1):
        A = (left_rotate((A ^ B), B % WORD_SIZE) + S[2 * i]) & 0xFFFFFFFF
        B = (left_rotate((B ^ A), A % WORD_SIZE) + S[2 * i + 1]) & 0xFFFFFFFF
    return struct.pack('<2I', A, B)

# Дешифрование
def decrypt(ciphertext, S):
    A, B = struct.unpack('<2I', ciphertext)
    for i in range(ROUNDS, 0, -1):
        B = right_rotate((B - S[2 * i + 1]) & 0xFFFFFFFF, A % WORD_SIZE) ^ A
        A = right_rotate((A - S[2 * i]) & 0xFFFFFFFF, B % WORD_SIZE) ^ B
    B = (B - S[1]) & 0xFFFFFFFF
    A = (A - S[0]) & 0xFFFFFFFF
    return struct.pack('<2I', A, B)

# Хеш-функция
def hash_function(message, key):
    S = key_schedule(key)
    H = 0  # Начальное значение хеша
    for i in range(0, len(message), 8):
        block = message[i:i+8]
        if len(block) < 8:
            block += b'\x00' * (8 - len(block))  # Дополнение блока до 8 байт
        M = int.from_bytes(block, 'little')
        M = M & 0xFFFFFFFF  # Ограничение до 32 бит
        H = H & 0xFFFFFFFF  # Ограничение до 32 бит
        H_new = int.from_bytes(encrypt(struct.pack('<2I', M ^ H, H), S), 'little')
        H = H_new ^ M ^ H
    return H

class RC5App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RC5 Cipher and Hash Function")

        # Создание виджетов
        self.label_message = QLabel("Введите сообщение:")
        self.entry_message = QLineEdit()

        self.label_key = QLabel("Введите ключ (16 символов):")
        self.entry_key = QLineEdit()

        self.encrypt_button = QPushButton("Зашифровать")
        self.decrypt_button = QPushButton("Расшифровать")
        self.hash_button = QPushButton("Вычислить хеш")

        self.result_label = QLabel("")

        self.copy_button = QPushButton("Копировать результат")

        layout = QGridLayout()
        layout.addWidget(self.label_message, 0, 0)
        layout.addWidget(self.entry_message, 0, 1)
        layout.addWidget(self.label_key, 1, 0)
        layout.addWidget(self.entry_key, 1, 1)
        layout.addWidget(self.encrypt_button, 2, 0)
        layout.addWidget(self.decrypt_button, 2, 1)
        layout.addWidget(self.hash_button, 3, 0)
        layout.addWidget(self.result_label, 4, 0, 1, 2)
        layout.addWidget(self.copy_button, 5, 0, 1, 2)

        self.setLayout(layout)

        self.encrypt_button.clicked.connect(self.encrypt)
        self.decrypt_button.clicked.connect(self.decrypt)
        self.hash_button.clicked.connect(self.compute_hash)
        self.copy_button.clicked.connect(self.copy_result)

    def encrypt(self):
        message = self.entry_message.text().encode()
        key = self.entry_key.text().encode()

        if len(key) != 16:
            QMessageBox.warning(
                self, "Ошибка", "Ключ должен быть длиной 16 символов")
            return

        # Генерация расширенного ключа
        S = key_schedule(key)

        # Дополнение сообщения до кратного 8 байтам
        padded_message = message + b' ' * (8 - len(message) % 8)

        # Шифрование блоков по 8 байт
        ciphertext = b''.join(
            encrypt(padded_message[i:i+8], S) for i in range(0, len(padded_message), 8))

        # Для удобства конвертировал в hex
        encrypted_hex = ciphertext.hex()
        self.result_label.setText(f"Зашифрованное сообщение: {encrypted_hex}")

    def decrypt(self):
        ciphertext_hex = self.entry_message.text()
        key = self.entry_key.text().encode()

        if len(key) != 16:
            QMessageBox.warning(
                self, "Ошибка", "Ключ должен быть длиной 16 символов")
            return

        # Генерация расширенного ключа
        S = key_schedule(key)

        # Конвертация из hex обратно в байты
        ciphertext = bytes.fromhex(ciphertext_hex)

        # Дешифрование блоков по 8 байт
        decrypted_message = b''.join(
            decrypt(ciphertext[i:i+8], S) for i in range(0, len(ciphertext), 8))

        # Убираю пробелы
        self.result_label.setText(
            f"Расшифрованное сообщение: {decrypted_message.decode().rstrip()}")

    def compute_hash(self):
        message = self.entry_message.text().encode()
        key = self.entry_key.text().encode()

        if len(key) != 16:
            QMessageBox.warning(
                self, "Ошибка", "Ключ должен быть длиной 16 символов")
            return

        # Вычисление хеша
        hash_value = hash_function(message, key)
        hash_hex = f"{hash_value:08x}"
        self.result_label.setText(f"Хеш: {hash_hex}")

    def copy_result(self):
        result_text = self.result_label.text()
        if "Зашифрованное сообщение:" in result_text:
            result_text = result_text.replace("Зашифрованное сообщение: ", "")
        elif "Расшифрованное сообщение:" in result_text:
            result_text = result_text.replace("Расшифрованное сообщение: ", "")
        elif "Хеш:" in result_text:
            result_text = result_text.replace("Хеш: ", "")
        clipboard = QApplication.clipboard()
        clipboard.setText(result_text)
        QMessageBox.information(self, "Скопировано",
                                "Результат скопирован в буфер обмена")

# Main
app = QApplication(sys.argv)
window = RC5App()
window.show()
sys.exit(app.exec_())