__author__ = "Ido Senn"

import Communication


class User:
    def __init__(self, socket, uname, email, aes_cypher):
        self.socket = socket
        self.uname = uname
        self.email = email
        self.aes_cypher = aes_cypher

    def get_uname(self):
        return self.uname

    def get_socket(self):
        return self.socket

    def get_email(self):
        return self.email

    def send_message(self, message):
        Communication.send_message_aes(self.socket, message, self.aes_cypher)

    def recv_message(self):
        return Communication.recv_message_aes(self.socket, self.aes_cypher)
