import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QGridLayout
from PyQt5.QtGui import QClipboard


class Enigma:
    def __init__(self, rotors, reflector):
        self.rotors = rotors  # Список роторов
        self.reflector = reflector  # Рефлектор
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Алфавит

# Метод шифрования сообщения
    def encrypt(self, message):
        result = []
        for char in message:
            if char in self.alphabet:
                self.rotate_rotors()
                for rotor in self.rotors:
                    char = rotor.forward(char)
                char = self.reflector[self.alphabet.index(char)]
                for rotor in reversed(self.rotors):
                    char = rotor.backward(char)
                result.append(char)
            else:
                result.append(char)
        return ''.join(result)


# Метод дешифрования сообщения

    def decrypt(self, message):
        result = []
        for char in message:
            if char in self.alphabet:
                self.rotate_rotors()
                for rotor in self.rotors:
                    char = rotor.forward(char)
                char = self.reflector[self.alphabet.index(char)]
                for rotor in reversed(self.rotors):
                    char = rotor.backward(char)
                result.append(char)
            else:
                result.append(char)
        return ''.join(result)


# Установка начальных позиций роторов с помощью ключа

    def set_key(self, key):
        for i, rotor in enumerate(self.rotors):
            rotor.set_position(key[i])

    def rotate_rotors(self):
        # Поворачиваем роторы
        for rotor in self.rotors:
            if not rotor.rotate():
                break


class Rotor:
    def __init__(self, wiring, notch):
        self.wiring = wiring
        self.notch = notch
        self.position = 0
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


    def set_position(self, position):
        self.position = self.alphabet.index(position)


    def rotate(self):
        self.position = (self.position + 1) % 26
        return self.position != self.alphabet.index(self.notch)


    def forward(self, char):
        index = (self.alphabet.index(char) + self.position) % 26
        return self.wiring[index]


    def backward(self, char):
        index = self.wiring.index(char)
        decoded_index = (index - self.position) % 26
        return self.alphabet[decoded_index]


# Настройка роторов и рефлектора
# Проводка и щель
rotors = [
    Rotor("EKMFLGDQVZNTOWYHXUSPAIBRCJ", 'Q'),
    Rotor("AJDKSIRUXBLHWTMCQGZNPYFVOE", 'E'),
    Rotor("BDFHJLCPRTXVZNYEIWGAKMUSQO", 'V'),
    Rotor("ESOVPZJAYQUIRHXLNFTGKDCMWB", 'J'),
    Rotor("VZBRGITYUPSDNHLXAWMJQOFECK", 'Z'),
    Rotor("JPGVOUMFYQBENHZRDKASXLICTW", 'M')
]

reflector = "YRUHQSLDPXNGOKMIEBFZCWVJAT"  # Настройки рефлектора
enigma = Enigma(rotors, reflector)  


class EnigmaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enigma Cipher")  

        # Создание виджетов
        # Метка для ввода сообщения
        self.label_message = QLabel("Введите сообщение:")
        self.entry_message = QLineEdit()  

        # Метка для ввода ключа
        self.label_key = QLabel("Введите ключ (6 символов):")
        self.entry_key = QLineEdit()  

        self.encrypt_button = QPushButton(
            "Зашифровать")  
        self.decrypt_button = QPushButton(
            "Расшифровать")  

        self.result_label = QLabel("")  


        self.copy_button = QPushButton("Копировать результат")


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


        self.encrypt_button.clicked.connect(self.encrypt)
        self.decrypt_button.clicked.connect(self.decrypt)
        self.copy_button.clicked.connect(self.copy_result)

    def encrypt(self):
        message = self.entry_message.text().upper()
        key = self.entry_key.text().upper()
        if len(key) != 6:
            QMessageBox.warning(
                self, "Ошибка", "Ключ должен быть длиной 6 символов")
            return
        enigma.set_key(key)
        encrypted_message = enigma.encrypt(message)
        self.result_label.setText(
            f"Зашифрованное сообщение: {encrypted_message}")

    def decrypt(self):
        message = self.entry_message.text().upper()
        key = self.entry_key.text().upper()
        if len(key) != 6:
            QMessageBox.warning(
                self, "Ошибка", "Ключ должен быть длиной 6 символов")
            return
        enigma.set_key(key)
        decrypted_message = enigma.decrypt(message)
        self.result_label.setText(
            f"Расшифрованное сообщение: {decrypted_message}")

    def copy_result(self):
        # Метод для копирования результата в буфер обмена
        result_text = self.result_label.text()

        # Убираем лишний текст перед копированием
        if "Зашифрованное сообщение:" in result_text:
            result_text = result_text.replace("Зашифрованное сообщение: ", "")
        elif "Расшифрованное сообщение:" in result_text:
            result_text = result_text.replace("Расшифрованное сообщение: ", "")

        clipboard = QApplication.clipboard()
        clipboard.setText(result_text)
        QMessageBox.information(self, "Скопировано",
                                "Результат с копирован в буфер обмена")


# Main
app = QApplication(sys.argv)
window = EnigmaApp()
window.show()
sys.exit(app.exec_())
