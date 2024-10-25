import tkinter as tk
from tkinter import messagebox

# Сам Алгоритм
# Функция шифрования
def string_conversion(str, step):
    new_str = ''
    for i in range(len(str)):
        k = 0
        while (str[i] != alfavit[k]):
            k += 1
        new_str += alfavit[(k + step) % len(alfavit)]
    return new_str


# Функция для обработки нажатия кнопки "Шифровать"
def encrypt_text():
    input_str = input_text.get().upper()
    step = int(step_entry.get())
    new_step = step_conversion(step)
    encrypted_str = string_conversion(input_str, new_step)
    encrypted_text.delete(0, tk.END)
    encrypted_text.insert(0, encrypted_str)


# Функция создающий новый сдвиг, чтобы он был положительным и находился в пределах длины алфавита
def step_conversion(step):
    if step < 0:
        new_step = abs(len(alfavit) + step)
    else:
        new_step = step
    return new_step


# Функция дешифрования
def deconv_str(str, step):
    new_str = ''
    for i in range(len(str)):
        k = 0
        while (str[i] != alfavit[k]):
            k += 1
        if (k - step < 0):
            new_str += alfavit[abs(len(alfavit) + k - step) % len(alfavit)]
        else:
            new_str += alfavit[(k - step) % len(alfavit)]
    return new_str


# Функция для обработки нажатия кнопки "Дешифровать"
def decrypt_text():
    input_str = encrypted_text.get()
    step = int(step_entry.get())
    decrypted_str = deconv_str(input_str, step)
    decrypted_text.delete(0, tk.END)
    decrypted_text.insert(0, decrypted_str)


# Функция выполняет частотный анализ строки и подсчитывает количество вхождений каждой буквы
def frequency_analysis(str):
    char_dict = dict()
    for char in str:
        if char in alfavit:
            if char in char_dict:
                char_dict[char] += 1
            else:
                char_dict[char] = 1
    return char_dict


# Функция разницы частот
def calculate_similarity(char_dict, eu_char_dict):
    check_difference = 0
    for index in alfavit:
        check_difference += abs(char_dict.get(index, 0) -
                                eu_char_dict.get(index, 0))
    return check_difference


# Функция взлома
def rest_cipher(encrypted_str):
    min_difference = float('inf')
    best_shift = 0
    best_decryption = ''
    for shift in range(len(alfavit)):
        decrypted_str = deconv_str(encrypted_str, shift)
        dict_char = frequency_analysis(decrypted_str)
        difference = calculate_similarity(dict_char, eu_char_dict)
        if difference < min_difference:
            min_difference = difference
            best_shift = shift
            best_decryption = decrypted_str
    return best_shift, best_decryption


# Функция для обработки нажатия кнопки "Взломать"
def vslom_cipher():
    input_str = encrypted_text.get()
    best_shift, best_decryption = rest_cipher(input_str)
    cracked_text.delete(0, tk.END)
    cracked_text.insert(0, best_decryption)
    shift_label.config(text=f"Лучший сдвиг: {best_shift}")
# Алфавит
alfavit = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
           "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

# Частота символов
eu_char_dict = {
    'A': 8.167, 'B': 1.492, 'C': 2.782, 'D': 4.253, 'E': 12.702, 'F': 2.228,
    'G': 2.015, 'H': 6.094, 'I': 6.966, 'J': 0.153, 'K': 0.772, 'L': 4.025,
    'M': 2.406, 'N': 6.749, 'O': 7.507, 'P': 1.929, 'Q': 0.095, 'R': 5.987, 'S': 6.327, 'T': 9.056, 'U': 2.758, 'V': 0.978, 'W': 2.360, 'X': 0.150,
    'Y': 1.974, 'Z': 0.074
}

#Интерфейс
root = tk.Tk()
root.title("Шифрование и расшифрование")
# Ввод строки
tk.Label(root, text="Введите строку:").grid(row=0, column=0)
input_text = tk.Entry(root, width=50)
input_text.grid(row=0, column=1)
# Ввод сдвига
tk.Label(root, text="Введите сдвиг:").grid(row=1, column=0)
step_entry = tk.Entry(root, width=10)
step_entry.grid(row=1, column=1)
# Кнопка шифрования
encrypt_button = tk.Button(root, text="Шифровать", command=encrypt_text)
encrypt_button.grid(row=2, column=0, columnspan=2)
# Зашифрованный текст
tk.Label(root, text="Зашифрованная строка:").grid(row=3, column=0)
encrypted_text = tk.Entry(root, width=50)
encrypted_text.grid(row=3, column=1)
# Кнопка дешифрования
decrypt_button = tk.Button(root, text="Расшифровать", command=decrypt_text)
decrypt_button.grid(row=4, column=0, columnspan=2)
# Расшифрованный текст
tk.Label(root, text="Расшифрованная строка:").grid(row=5, column=0)
decrypted_text = tk.Entry(root, width=50)
decrypted_text.grid(row=5, column=1)
# Кнопка взлома
crack_button = tk.Button(root, text="Взломать", command=vslom_cipher)
crack_button.grid(row=6, column=0, columnspan=2)
# Взломанная строка
tk.Label(root, text="Взломанная строка:").grid(row=7, column=0)
cracked_text = tk.Entry(root, width=50)
cracked_text.grid(row=7, column=1)
# Метка для отображения лучшего сдвига
shift_label = tk.Label(root, text="Лучший сдвиг: ")
shift_label.grid(row=8, column=0, columnspan=2)
root.mainloop()