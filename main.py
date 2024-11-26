import sys
import struct
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox
)

# Константы RC5
WORD_SIZE = 32
ROUNDS = 12
KEY_SIZE = 16
P = 0xB7E15163
Q = 0x9E3779B9

# Функция для циклического сдвига влево
def left_rotate(value, shift):
    return ((value << shift) & 0xFFFFFFFF) | (value >> (WORD_SIZE - shift))

# Функция для циклического сдвига вправо
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
        B = L[j] = left_rotate((L[j] + A + B) & 0xFFFFFFFF, (A + B) % WORD_SIZE)
        i = (i + 1) % len(S)
        j = (j + 1) % len(L)
    return S

# Шифрование блока
def encrypt(block, S):
    A, B = struct.unpack('<2I', block)
    A = (A + S[0]) & 0xFFFFFFFF
    B = (B + S[1]) & 0xFFFFFFFF
    for i in range(1, ROUNDS + 1):
        A = (left_rotate((A ^ B), B % WORD_SIZE) + S[2 * i]) & 0xFFFFFFFF
        B = (left_rotate((B ^ A), A % WORD_SIZE) + S[2 * i + 1]) & 0xFFFFFFFF
    return struct.pack('<2I', A, B)

# Генерация потока ключей
def generate_keystream(S, length, iv):
    keystream = b''
    block = iv
    while len(keystream) < length:
        block = encrypt(block, S)
        keystream += block
    return keystream[:length]

# Главное приложение
class RC5StreamApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RC5 Stream Cipher")

        # Создание виджетов
        self.label_message = QLabel("Введите сообщение:")
        self.entry_message = QLineEdit()

        self.label_key = QLabel("Введите ключ (16 символов):")
        self.entry_key = QLineEdit()

        self.encrypt_button = QPushButton("Зашифровать")
        self.decrypt_button = QPushButton("Расшифровать")

        self.result_label = QLabel("")

        self.copy_button = QPushButton("Копировать результат")

        # Расположение виджетов
        layout = QGridLayout()
        layout.addWidget(self.label_message, 0, 0)
        layout.addWidget(self.entry_message, 0, 1)
        layout.addWidget(self.label_key, 1, 0)
        layout.addWidget(self.entry_key, 1, 1)
        layout.addWidget(self.encrypt_button, 2, 0)
        layout.addWidget(self.decrypt_button, 2, 1)
        layout.addWidget(self.result_label, 3, 0, 1, 2)
        layout.addWidget(self.copy_button, 4, 0, 1, 2)

        self.setLayout(layout)

        # Подключение событий
        self.encrypt_button.clicked.connect(self.encrypt)
        self.decrypt_button.clicked.connect(self.decrypt)
        self.copy_button.clicked.connect(self.copy_result)

    def encrypt(self):
        message = self.entry_message.text().encode()
        key = self.entry_key.text().encode()

        if len(key) != 16:
            QMessageBox.warning(self, "Ошибка", "Ключ должен быть длиной 16 символов")
            return

        # Генерация расширенного ключа
        S = key_schedule(key)

        # Инициализационный вектор
        iv = b'\x00' * 8

        # Генерация псевдослучайного потока
        keystream = generate_keystream(S, len(message), iv)

        # Шифрование (XOR с потоком ключей)
        ciphertext = bytes(m ^ k for m, k in zip(message, keystream))

        # Конвертация в hex для удобства отображения
        encrypted_hex = ciphertext.hex()
        self.result_label.setText(f"Зашифрованное сообщение: {encrypted_hex}")

    def decrypt(self):
        ciphertext_hex = self.entry_message.text()
        key = self.entry_key.text().encode()

        if len(key) != 16:
            QMessageBox.warning(self, "Ошибка", "Ключ должен быть длиной 16 символов")
            return

        # Генерация расширенного ключа
        S = key_schedule(key)

        # Конвертация из hex обратно в байты
        ciphertext = bytes.fromhex(ciphertext_hex)

        # Инициализационный вектор
        iv = b'\x00' * 8

        # Генерация псевдослучайного потока
        keystream = generate_keystream(S, len(ciphertext), iv)

        # Дешифрование (XOR с потоком ключей)
        decrypted_message = bytes(c ^ k for c, k in zip(ciphertext, keystream))

        self.result_label.setText(
            f"Расшифрованное сообщение: {decrypted_message.decode(errors='ignore')}"
        )

    def copy_result(self):
        result_text = self.result_label.text()
        if "Зашифрованное сообщение:" in result_text:
            result_text = result_text.replace("Зашифрованное сообщение: ", "")
        elif "Расшифрованное сообщение:" in result_text:
            result_text = result_text.replace("Расшифрованное сообщение: ", "")
        clipboard = QApplication.clipboard()
        clipboard.setText(result_text)
        QMessageBox.information(self, "Скопировано", "Результат скопирован в буфер обмена")


# Запуск приложения
app = QApplication(sys.argv)
window = RC5StreamApp()
window.show()
sys.exit(app.exec_())
