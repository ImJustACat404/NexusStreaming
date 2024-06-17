__author__ = "Ido Senn"

import socket
import msgpack
import AESEncrypt
from AESEncrypt import AESCypher
import RsaService

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


def send_message_unsecure(sock, message):
    """
    Sand an unencrypted message
    :param sock: A socket to sand the message to
    :type sock: socket.socket
    :param message: A message to send
    :type message: dict
    """
    # print("[--->]" + str(message)[:100])
    packed_message = msgpack.packb(message)  # serialize dictionary
    sock.sendall(str(len(packed_message)).zfill(LEN_LEN).encode() + packed_message)  # send data with length


def recv_message_unsecure(sock):
    """
    Receive an unencrypted message
    :param sock: A socket to receive a message from
    :type sock: socket.socket
    :return: A message
    :rtype: dict
    """
    message_length = int(sock.recv(LEN_LEN).decode())
    message = msgpack.unpackb(_recvall(sock, message_length))  # deserialize dictionary
    # print("[<---]" + str(message)[:100])
    return message


def send_message_rsa(sock, message, public_key):
    """
    Send a message encrypted with RSA
    :param sock: A socket to send the message to
    :type sock: socket.socket
    :param message: A message to send
    :type message: dict
    :param public_key: the public RSA key used for encryption
    :type public_key: public RSA key
    """
    # print("[--->]" + str(message)[:100])
    packed_message = msgpack.packb(message)  # serialize dictionary
    encrypted_message = RsaService.rsa_encrypt(packed_message, public_key)  # Encrypt data with RSA
    sock.sendall(str(len(encrypted_message)).zfill(LEN_LEN).encode() + encrypted_message)  # send data with length


def recv_message_rsa(sock, private_key):
    """
    Receive a message encrypted with RSA
    :param sock: A socket to receive a message from
    :type sock: socket.socket
    :param private_key: The private RSA key, used for decryption
    :type private_key: private RSA key
    :return: A message
    :rtype: dict
    """
    message_length = int(sock.recv(LEN_LEN).decode())
    encrypted_message = _recvall(sock, message_length)
    packed_message = RsaService.rsa_decrypt(encrypted_message, private_key)  # decrypt data with RSA
    message = msgpack.unpackb(packed_message)  # deserialize dictionary
    # print("[<---]" + str(message)[:100])
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
    # print("[--->]" + str(message)[:100])
    packed_message = msgpack.packb(message)  # serialize dictionary
    encrypted_message = cypher.aes_encrypt(packed_message)  # Encrypt data with aes
    sock.sendall(str(len(encrypted_message)).zfill(LEN_LEN).encode() + encrypted_message)  # send data with length


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
    packed_message = cypher.aes_decrypt(encrypted_message)  # Decrypt data with AES
    message = msgpack.unpackb(packed_message)  # deserialize dictionary
    # print("[<---]" + str(message)[:100])
    return message
