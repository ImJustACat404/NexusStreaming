__author__ = "Ido Senn"

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


def generate_key():
    # Generate a random 256-bit (32-byte) key
    return get_random_bytes(32)


def generate_iv():
    # Generate a random 128-bit (16-byte) IV
    return get_random_bytes(16)


class AESCypher:
    def __init__(self, iv, aes_key):
        self.aes_key = aes_key
        self.iv = iv

    def aes_encrypt(self, message_bytes):
        # Create an AES cipher object with the provided key, AES.MODE_CBC mode, and the given IV
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.iv)
        # Pad the plaintext to match the block size (128 bits or 16 bytes for AES)
        padded_data = pad(message_bytes, AES.block_size)
        # Encrypt the padded plaintext
        encrypted_message_bytes = cipher.encrypt(padded_data)
        return encrypted_message_bytes

    def aes_decrypt(self, encrypted_message_bytes):
        # Create an AES cipher object with the provided key, AES.MODE_CBC mode, and the given IV
        cipher = AES.new(self.aes_key, AES.MODE_CBC, self.iv)
        # Decrypt the ciphertext
        decrypted_data = cipher.decrypt(encrypted_message_bytes)
        # Unpad the decrypted data
        message_bytes = unpad(decrypted_data, AES.block_size)
        return message_bytes

obj = AESCypher(generate_iv(), generate_key())