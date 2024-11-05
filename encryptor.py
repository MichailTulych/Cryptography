import struct

WORD_SIZE = 32
ROUNDS = 12
KEY_SIZE = 16
P = 0xB7E15163
Q = 0x9E3779B9


def left_rotate(value, shift):
    return ((value << shift) & 0xFFFFFFFF) | (value >> (WORD_SIZE - shift))


def right_rotate(value, shift):
    return ((value >> shift) | (value << (WORD_SIZE - shift))) & 0xFFFFFFFF


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


def pad(data):
    padding_length = (8 - len(data) % 8) % 8
    return data + b'\x00' * padding_length


def unpad(data):
    return data.rstrip(b'\x00')


def encrypt(plaintext, S):
    plaintext = pad(plaintext)  # Дополнение
    encrypted = b""
    for i in range(0, len(plaintext), 8):
        block = plaintext[i:i+8]
        encrypted += _encrypt_block(block, S)
    return encrypted


def decrypt(ciphertext, S):
    decrypted = b""
    for i in range(0, len(ciphertext), 8):
        block = ciphertext[i:i+8]
        decrypted += _decrypt_block(block, S)
    return unpad(decrypted)  # Удаление дополнения


def _encrypt_block(block, S):
    A, B = struct.unpack('<2I', block)
    A = (A + S[0]) & 0xFFFFFFFF
    B = (B + S[1]) & 0xFFFFFFFF
    for i in range(1, ROUNDS + 1):
        A = (left_rotate((A ^ B), B % WORD_SIZE) + S[2 * i]) & 0xFFFFFFFF
        B = (left_rotate((B ^ A), A % WORD_SIZE) + S[2 * i + 1]) & 0xFFFFFFFF
    return struct.pack('<2I', A, B)


def _decrypt_block(block, S):
    A, B = struct.unpack('<2I', block)
    for i in range(ROUNDS, 0, -1):
        B = right_rotate((B - S[2 * i + 1]) & 0xFFFFFFFF, A % WORD_SIZE) ^ A
        A = right_rotate((A - S[2 * i]) & 0xFFFFFFFF, B % WORD_SIZE) ^ B
    B = (B - S[1]) & 0xFFFFFFFF
    A = (A - S[0]) & 0xFFFFFFFF
    return struct.pack('<2I', A, B)
