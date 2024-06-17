from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA


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


def rsa_encrypt(data, public_key):
    """
    A function that encrypts a message using RSA
    :param data: The data to encrypt
    :type data: bytes
    :param public_key: The public RSA key, used for encryption
    :type public_key: public RSA key
    :return: The encrypted data
    :rtype: bytes
    """
    rsa_cypher = PKCS1_OAEP.new(RSA.importKey(public_key))
    encrypted_data = rsa_cypher.encrypt(data)
    return encrypted_data


def rsa_decrypt(data, private_key):
    """
    A function that decrypts a message using RSA
    :param data: The data to decrypt
    :type data: bytes
    :param private_key: The private RSA key, used for decryption
    :type private_key: private RSA key
    :return: The decrypted data
    :rtype: bytes
    """
    rsa_cypher = PKCS1_OAEP.new(RSA.importKey(private_key))
    decrypted_data = rsa_cypher.decrypt(data)
    return decrypted_data
