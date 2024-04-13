import socket
import msgpack
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import AESEncrypt
from AESEncrypt import AESCypher

LEN_LEN = 8  # Length of length buffer


def _recvall(sock, size):
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
    key = RSA.generate(2048)  # generate pair of keys
    public_key = key.public_key().export_key('PEM')
    private_key = key.export_key()
    return private_key, public_key, key


def send_message_unsecure(sock, message):
    print("[--->]" + str(message)[:100])
    packed_message = msgpack.packb(message)
    sock.sendall(str(len(packed_message)).zfill(LEN_LEN).encode() + packed_message)


def recv_message_unsecure(sock):
    message_length = int(sock.recv(LEN_LEN).decode())
    message = msgpack.unpackb(_recvall(sock, message_length))
    print("[<---]" + str(message)[:100])
    return message


def send_message_rsa(sock, message, cypher):
    print("[--->]" + str(message)[:100])
    packed_message = msgpack.packb(message)
    encrypted_message = cypher.encrypt(packed_message)
    sock.sendall(str(len(encrypted_message)).zfill(LEN_LEN).encode() + encrypted_message)


def recv_message_rsa(sock, cypher):
    message_length = int(sock.recv(LEN_LEN).decode())
    encrypted_message = _recvall(sock, message_length)
    packed_message = cypher.decrypt(encrypted_message)
    message = msgpack.unpackb(packed_message)
    print("[<---]" + str(message)[:100])
    return message


def send_message_aes(sock, message, cypher):
    """

    :param sock:
    :param message:
    :param cypher:
    :type cypher: AESCypher
    :return:
    """
    print("[--->]" + str(message)[:100])
    packed_message = msgpack.packb(message)
    encrypted_message = cypher.aes_encrypt(packed_message)
    sock.sendall(str(len(encrypted_message)).zfill(LEN_LEN).encode() + encrypted_message)


def recv_message_aes(sock, cypher):
    """

    :param sock:
    :param cypher:
    :type cypher: AESCypher
    :return:
    """
    message_length = int(sock.recv(LEN_LEN).decode())
    encrypted_message = _recvall(sock, message_length)
    packed_message = cypher.aes_decrypt(encrypted_message)
    message = msgpack.unpackb(packed_message)
    print("[<---]" + str(message)[:100])
    return message
