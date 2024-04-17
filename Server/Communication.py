__author__ = "Ido Senn"

import socket
import msgpack
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import AESEncrypt
from AESEncrypt import AESCypher

LEN_LEN = 8  # Length of length buffer


def _recvall(sock, size):
    """
    A function that receives a given amount of bytes from a socket. Ensures that all the expected data from a network
    stream is received and returned as a whole.
    :param sock: A socket to read from
    :type sock: socket.socket
    :param size: Number of bytes to read
    :type size: int
    :return: The data received from the socket
    :rtype: bytes
    """
    data = b''  # Initialize an empty byte string to store received data
    while len(data) < size:
        # Receive data in chunks
        chunk = sock.recv(size - len(data))
        if not chunk:
            # Handle the case where the connection is closed
            raise RuntimeError("Socket connection closed prematurely")
        data += chunk
    return data


def generate_rsa_keys():
    """
    A function that generates a pair of random RSA public and private keys
    :return: A tuple with the private and public RSA keys (prv, pub)
    :rtype: tuple
    """
    key = RSA.generate(2048)  # generate a pair of keys
    public_key = key.public_key().export_key('PEM')
    private_key = key.export_key()
    return private_key, public_key


def send_message_unsecure(sock, message):
    """
    Sand an unencrypted message
    :param sock: A socket to sand the message to
    :type sock: socket.socket
    :param message: A message to send
    :type message: dict
    """
    print("[--->]" + str(message)[:100])
    packed_message = msgpack.packb(message)
    sock.sendall(str(len(packed_message)).zfill(LEN_LEN).encode() + packed_message)


def recv_message_unsecure(sock):
    """
    Receive an unencrypted message
    :param sock: A socket to receive a message from
    :type sock: socket.socket
    :return: A message
    :rtype: dict
    """
    message_length = int(sock.recv(LEN_LEN).decode())
    message = msgpack.unpackb(_recvall(sock, message_length))
    print("[<---]" + str(message)[:100])
    return message


def send_message_rsa(sock, message, cypher):
    """
    Send a message encrypted with RSA
    :param sock: A socket to send the message to
    :type sock: socket.socket
    :param message: A message to send
    :type message: dict
    :param cypher: An object used to encrypt data with RSA
    :type cypher: Crypto.Cipher.PKCS1_OAEP.PKCS1OAEP_Cipher
    """
    print("[--->]" + str(message)[:100])
    packed_message = msgpack.packb(message)
    encrypted_message = cypher.encrypt(packed_message)
    sock.sendall(str(len(encrypted_message)).zfill(LEN_LEN).encode() + encrypted_message)


def recv_message_rsa(sock, cypher):
    """
    Receive a message encrypted with RSA
    :param sock: A socket to receive a message from
    :type sock: socket.socket
    :param cypher: An object used to decrypt messages with RSA
    :type cypher: Crypto.Cipher.PKCS1_OAEP.PKCS1OAEP_Cipher
    :return: A message
    :rtype: dict
    """
    message_length = int(sock.recv(LEN_LEN).decode())
    encrypted_message = _recvall(sock, message_length)
    packed_message = cypher.decrypt(encrypted_message)
    message = msgpack.unpackb(packed_message)
    print("[<---]" + str(message)[:100])
    return message


def send_message_aes(sock, message, cypher):
    """
    Send a message encrypted with AES
    :param sock: A socket to send a message to
    :type sock: socket.socket
    :param message: A message to send
    :type message: dict
    :param cypher: An object used to encrypt and decrypt data using AES
    :type cypher: AESCypher
    """
    print("[--->]" + str(message)[:100])
    packed_message = msgpack.packb(message)
    encrypted_message = cypher.aes_encrypt(packed_message)
    sock.sendall(str(len(encrypted_message)).zfill(LEN_LEN).encode() + encrypted_message)


def recv_message_aes(sock, cypher):
    """
    Receive a message encrypted with AES
    :param sock: A socket to receive a message from
    :type sock: socket.socket
    :param cypher: An object used to encrypt and decrypt data using AES
    :type cypher: AESCypher
    :return: A message
    :rtype: dict
    """
    message_length = int(sock.recv(LEN_LEN).decode())
    encrypted_message = _recvall(sock, message_length)
    packed_message = cypher.aes_decrypt(encrypted_message)
    message = msgpack.unpackb(packed_message)
    print("[<---]" + str(message)[:100])
    return message
