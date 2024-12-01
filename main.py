import sys
import struct
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox
)
# Константы RC5
ROUNDS = 12
P = 0xB7E15163
Q = 0x9E3779B9

# Функция для циклического сдвига влево
def left_rotate(value, shift):
    bit_length = value.bit_length()  # Получаю битовую длину числа
    shift = shift % bit_length
    return (value << shift) | (value >> (bit_length - shift))

# Функция для циклического сдвига вправо
def right_rotate(value, shift):
    bit_length = value.bit_length()
    shift = shift % bit_length
    return ((value >> shift) | (value << (bit_length - shift))) 

# Генерация расширенного ключа
def key_schedule(key):
    L = [int.from_bytes(key[i:i+4], 'little') for i in range(0, len(key), 4)]
    S = [P]
    for i in range(1, 2 * ROUNDS + 2):
        S.append(S[i - 1] + Q)
    i = j = A = B = 0
    for k in range(3 * max(len(L), len(S))):
        A = S[i] = left_rotate(S[i] + A + B, 3)
        B = L[j] = left_rotate(L[j] + A + B, (A + B) % 32)
        i = (i + 1) % len(S)
        j = (j + 1) % len(L)
    return S

# Шифрование блока
def encrypt(plaintext, S):
    A, B = struct.unpack('<2I', plaintext)
    A = (A + S[0])& 0xFFFFFFFF
    B = (B + S[1])& 0xFFFFFFFF
    for i in range(1, ROUNDS + 1):
        A = (left_rotate(A ^ B, B % 32) + S[2 * i])& 0xFFFFFFFF
        B = (left_rotate(B ^ A, A % 32) + S[2 * i + 1])& 0xFFFFFFFF
    return struct.pack('<2I', A, B)

def decrypt(ciphertext, S):
    A, B = struct.unpack('<2I', ciphertext)
    for i in range(ROUNDS, 0, -1):
        B = (right_rotate(B - S[2 * i + 1], A % 32) ^ A)& 0xFFFFFFFF
        A = (right_rotate(A - S[2 * i], B % 32) ^ B)& 0xFFFFFFFF
    B = (B - S[1])& 0xFFFFFFFF
    A = (A - S[0])& 0xFFFFFFFF
    return struct.pack('<2I', A, B)

# Генерация ключа равной длины
def extend_key(key, length):
    key = (key * (length // len(key) + 1))[:length]
    return key

# Генерация потока ключей
def generate_keystream(S, length):
    keystream = b''
    block = b'\x00'*8
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

        self.label_key = QLabel("Введите ключ:")
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

        if not key:
            QMessageBox.warning(self, "Ошибка", "Ключ  не должен быть пустым")
            return

        #Приведение ключа к длине сообщения 
        key = extend_key(key, len(message))

        # Генерация расширенного ключа
        S = key_schedule(key)

        # Генерация псевдослучайного потока
        keystream = generate_keystream(S, len(message))

        # Шифрование (XOR с потоком ключей)
        ciphertext = bytes(m ^ k for m, k in zip(message, keystream))
        self.result_label.setText(f"Зашифрованное сообщение: {ciphertext.hex()}")

    def decrypt(self):
        ciphertext_hex = self.entry_message.text()
        key = self.entry_key.text().encode()

        if not key:
            QMessageBox.warning(self, "Ошибка", "Ключ не должен быть пустым")
            return
        
        # Приведение ключа к длине сообщения
        ciphertext = bytes.fromhex(ciphertext_hex)
        key = extend_key(key, len(ciphertext))

        # Генерация расширенного ключа
        S = key_schedule(key)

        # Генерация псевдослучайного потока
        keystream = generate_keystream(S, len(ciphertext))
        
        # Дешифрование (XOR с потоком ключей)
        decrypted_message = bytes([c ^ k for c, k in zip(ciphertext, keystream)])

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
