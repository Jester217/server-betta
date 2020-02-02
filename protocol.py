# -*- coding: utf-8 -*-
import socket

NAME_LENGTH = 2
COMMAND_LENGTH = 1
DATA_LENGTH = 7
MESSAGE_LENGTH = 7

COMMANDS = {
    "1": [MESSAGE_LENGTH],
    "2": [NAME_LENGTH],
    "3": [NAME_LENGTH],
    "4": [NAME_LENGTH],
    "5": [NAME_LENGTH, MESSAGE_LENGTH],
    "7": [],
}


"""
CR (misha): 
    Well this entire file is a mess, i am a bit tired so ill leave it to the next iteration of the CR
    Try making it look good next time
    
    sry :|
     still relevnt?
"""

def get_name(sock):
    try:
        name = get_username(sock)
        command = get_command(sock)
        get_args(sock, command)
        return name
    except socket.error:
        return ""


def get_request(sock):
    """
    get a request from a client socket
    Works with the protocol defined in the client's "send_request_to_server" function

    :param sock: The socket to send the message to
    :type sock: socket.socket

    :return: name, command, args
    :rtype: string, string, list

    Example:
            NAME_LENGTH = 2, COMMAND_LENGTH = 1, DATA_LENGTH = 7
            04Omer10000018This is an example --> name=omer, command = 1, args = This is an example
    """
    try:
        username = get_username(sock)
        command = get_command(sock)
        args = get_args(sock, command)
        return username, command, args

    except socket.error:
        return ""



def get_username(sock):
    """
    get a username from a client socket
    Works with the protocol defined in the client's "send_request_to_server" function

    :param sock: The socket to send the message to
    :type sock: socket.socket

    :return: name
    :rtype: string

    Example:
            NAME_LENGTH = 2
            04Omer --> Omer
    """
    try:
        name_length = sock.recv(NAME_LENGTH)
        if name_length == "":
            return ""

        if not (name_length.isdigit() and name_length > 0):
            return []
        return r'{}'.format(sock.recv(int(name_length)))
    except socket.error:
        return ""


def get_command(sock):
    """
    get a command from a client socket
    Works with the protocol defined in the client's "send_request_to_server" function
    in this case the command is a single digit number

    :param sock: The socket to send the message to
    :type sock: socket.socket

    :return: command
    :rtype: string

    Example:
            COMMAND_LENGTH = 1
    """
    try:
        command = sock.recv(int(COMMAND_LENGTH))
        if not command in COMMANDS.keys():
            return ""
        return r'{}'.format(command)
    except socket.error:
        return ""


def get_args(sock, command):
    """
    get a args from a client socket according to command
    Works with the protocol defined in the client's "send_request_to_server" function
    in this case the command is a single digit number

    :param sock: The socket to send the message to
    :type sock: socket.socket

    :return: command
    :rtype: string

    Example:
            COMMAND_LENGTH = 1
    """
    args = []
    args_lengths = COMMANDS.get(command)
    if not args_lengths:
        return
    for length in args_lengths:
        length = sock.recv(length)
        if not (length.isdigit() and length >= 0):
            return
        args.append(r"{}".format(sock.recv(int(length))))
    return args


def send_message(sock, message):
    """
    Constructs a message according to the server's protocol and send it to a given socket

    :param sock: The socket to send the message to
    :type sock: socket.socket
    :param message: The message to send
    :type message: str

    :return: True if the send was successful
    :rtype: bool
    """
    length = str(len(message)).zfill(MESSAGE_LENGTH)
    try:
        sock.send(length)
        sock.send(message)
        return True
    except socket.error:
        return False


def main():
    """
    Add Documentation here
    """
    pass  # Replace Pass with Your Code


if __name__ == '__main__':
    main()