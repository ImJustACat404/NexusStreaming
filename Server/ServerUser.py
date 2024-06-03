__author__ = "Ido Senn"

import Communication
import select


class User:
    def __init__(self, socket, uname, email, aes_cypher):
        self.socket = socket
        self.uname = uname
        self.email = email
        self.aes_cypher = aes_cypher

    def get_uname(self):
        """
        A function that returns the user's name
        :return: username
        :rtype: str
        """
        return self.uname

    def get_socket(self):
        """
        A function that returns the user's socket
        :return: user's socket
        :rtype: socket.socket
        """
        return self.socket

    def get_email(self):
        """
        A function that returns the user's email address
        :return: user's email
        :rtype: str
        """
        return self.email

    def send_message(self, message):
        """
        A function that sends an encrypted message to the user
        :param message: A message to send
        :type message: dict
        """
        Communication.send_message_aes(self.socket, message, self.aes_cypher)

    def recv_message(self):
        """
        A function that receives an encrypted message from the user
        :return: The message
        :rtype: dict
        """
        return Communication.recv_message_aes(self.socket, self.aes_cypher)

    def close_socket(self):
        """
        Close the client's socket
        """
        self.socket.close()


def user_select(connected_users_dict, rlist, wlist, xlist):
    """
    Preforms "select" on a list of sockets and returns list of read users, write users, and error users.
    Sometimes in the server users are saved as sockets to reduce time converting them back to sockets every select
    :param connected_users_dict:
    :param rlist: A list of sockets to read from
    :type rlist: list
    :param wlist: A list of sockets to write to
    :type wlist: list
    :param xlist: A list of sockets to check for errors
    :type xlist: list
    :return: A list of users available for reading, for writing, and ones that are in error
    :rtype: tuple
    """
    read_sockets, write_sockets, error_sockets = select.select(rlist, wlist, xlist)
    read_users = []
    write_users = []
    error_users = []
    for socket in read_sockets:
        read_users += [connected_users_dict[socket]]
    for socket in write_sockets:
        write_users += [connected_users_dict[socket]]
    for socket in error_sockets:
        error_users += [connected_users_dict[socket]]
    return read_users, write_users, error_users
