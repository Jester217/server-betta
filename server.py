import socket
import select
import logging
import sys
#from . import protocol
#from . import server_ascii
import protocol
import server_ascii
from datetime import datetime

"""
CR (misha): 
    It is a good practice to use UPPERCASE variables as const-like variables
    And lowercase for global variables, 
    also consider adding some king of indication this is a global variable (e.g g_muted_clients)
    
    Consider splitting the CONST "config like" variables and the globals so it will be clear 
    because not this is just a huge mess       
    
    if after reading all the CR i have left you here you still decide to keep the globals then add documentation
"""

LOGGING_STATE = logging.INFO
DEBUG = False
HARD_THROW = False  # if switched on in delete user delete from Admin and Mute lists
PRINT_PRIVATE_MESSAGES = False
SERVER = ("0.0.0.0", 1337)
MAX_CLIENT = 5
NAME_LENGTH = 2
OPEN_CLIENT_SOCKETS = []
CLIENTS = {  # user name, socket

}
MASTER_ADMIN = ("Ro'i", "127.0.0.1")
ADMINS = [MASTER_ADMIN[0]]  # [user name]
MUTED_CLIENTS = []
MESSAGES_TO_SEND = []
ADMIN_COMMANDS = ["2", "3", "4"]
ADMIN_SYMBOL = "@"
FORBIDDEN_CHARACTERS = ["\"", "/", ]

"""
CR (misha): Add docstring for all the functions ( there is none ) 
    *** i have added one for example in the protocol.send_message function***
"""

"""
CR (misha): 
    I dont like when code uses globals,
    for now it is not awful but when/if you will add multi-threading  this will bite you in the ass
    
    There are 3 arguments against using globals:
        1. multi-threading
        2. it is easy to confuse functions that change state with those that return value ( there are few in this file)
        3. if you will want to make this project a lib then the one that uses you could not have more then one 
           instance of this server at the same time
               
"""


def broadcast(name, data):
    message = message_format(name, data)
    MESSAGES_TO_SEND.append((name, message, False))


def add_admin(commander, name):
    if name not in CLIENTS or name in ADMINS:
        return
    ADMINS.append(name)
    logging.info(name)
    message = "Now an admin {0} is. Use the Force, {0}\n".format(name)
    MESSAGES_TO_SEND.append((commander, message, False))


def kick(commander, name):
    if name not in CLIENTS or name == MASTER_ADMIN[0]:
        return
    """
    CR (misha): ???
    """
    logging.info(CLIENTS.keys())
    for k in CLIENTS.keys():
        if k == name:
            OPEN_CLIENT_SOCKETS.remove(CLIENTS[k])
            del CLIENTS[k]
    logging.info(CLIENTS.keys())

    """
    CR (misha): 
        What will happen if ill ask you to add more attributes to a client ( in addition to mute and admin)?
        Will you add a list for each one? 
        quickly counting i can count 3 places you need to change each time! 
    """

    if name in ADMINS and name != MASTER_ADMIN[0]:
        ADMINS.remove(name)

    if name in MUTED_CLIENTS:
        MUTED_CLIENTS.remove(name)
    message = "Been kicked from the chat {} has!\n".format(name)
    MESSAGES_TO_SEND.append((commander, message, False))


def mute(commander, name):
    if name not in CLIENTS or name == MASTER_ADMIN[0]:
        return
    if name in MUTED_CLIENTS:
        MUTED_CLIENTS.remove(name)
        message = "No longer muted {} is.\n".format(name)
        MESSAGES_TO_SEND.append((commander, message, False))
        return
    MUTED_CLIENTS.append(name)
    message = "Muted now {} is.\n".format(name)
    MESSAGES_TO_SEND.append((commander, message, False))


def private(name, recipient, message):
    recipient_socket = CLIENTS.get(recipient)
    if not recipient_socket:
        return

    message = "!" + message_format(name, message)
    MESSAGES_TO_SEND.append((name, message, recipient_socket))


def star_wars(name):
    message = server_ascii.message_ascii()
    MESSAGES_TO_SEND.append(("server", message, CLIENTS[name]))


def quit_command(name):
    delete_client(CLIENTS[name])


def view_managers(name):
    """
    CR (misha): Rewrite this function and add documentation
    """
    """
    CR (misha):
        I dont like that you save the admin name with te prefix
        even more i dont like that you do this hard coded shit here
        what will happen if the admin prefix whould be `~@` instead of just `@`
    """
    message = "Managers are: " + str(ADMINS)[1:-1] + "\n"
    MESSAGES_TO_SEND.append(("server", message, CLIENTS[name]))


def view_commands(name):
    message = "Commands are: "
    for command in COMMANDS.values():
        message += "{}, ".format(command.__name__)

    message += "\n"
    MESSAGES_TO_SEND.append(("server", message, CLIENTS[name]))


SPECIAL_MESSAGES = {
    "quit": quit_command,
    "view-managers": view_managers,
    "view-commands": view_commands,
}

COMMANDS = {
    "1": broadcast,
    "2": add_admin,
    "3": kick,
    "4": mute,
    "5": private,
    "6": view_managers,
    "7": star_wars,
}

"""
CR (misha): i dont know if start server is the correct name, to me it seems like construct server

BTW if a the name of a function is start_server the documentation "function starts server" if an bad name
"""


def start_server(ip, port):
    """
    function starts server
    """
    """
    CR (misha): 
        it seems like the arguments like SERVER[0], SERVER[1], MASTER_ADMIN[0] and MAX_CLIENT
        could pass as arguments to the function instead of global access 
    """
    """
    CR (misha): 
        This 'if' is a good example why you need to pass them as arguments to the function
        raw_input should not be here
    """
    server_socket = socket.socket()
    try:
        server_socket.bind((ip, port))
    except socket.error:
        """
        CR (misha): Why wrapping exceptions here with a custom message, why not let it raise?
        """
        logging.info(socket.error)
        server_socket.close()
        return False, ""
        """
        CR (misha): 
            exiting inside an internal function using os.exit is brutal 
            you dont even give the caller a chance to handle the error 
            (what if he has some open resources that he needs to close)  
        """
    server_socket.listen(MAX_CLIENT)
    """
    CR (misha): I know it seems cool to have a cool banner here but it is really should not be here
    """
    server_ascii.server_ascii()
    """
    CR (misha): Consider using the logging module instead of unconditional prints in the middle of the code 
    """
    logging.info("Up server is.\nIP address {0} Port {1}\nMAY THE FORCE BE WITH YOU, {2}\n".format(ip, port, MASTER_ADMIN[0]))
    return True, server_socket


def get_new_client(server_socket):
    try:
        sock, address = server_socket.accept()
    except socket.error:
        return
    OPEN_CLIENT_SOCKETS.append(sock)
    if DEBUG:
        logging.info("new socket have connected \nip: {0}, port: {1}\n".format(address[0], address[1]))
        logging.info("sock: " + str(sock))


def handle_client(client_sock):
    request = get_request(client_sock)

    """
    CR (misha):
        while returning empty sting instead of an object/list throwing an exception could be more elegant
        Read more inside the delete client function
    """
    if request == "":  # this section delete client if socket closed
        delete_client(client_sock)
        return

    if not valid_request(request, client_sock):  # ignore request if not valid or illegal
        return

    handle_request(request)  # this section handle the legit requests


def get_name(new_socket):
    name = (protocol.get_name(new_socket)).strip()

    if name == "":
        return name

    if not valid_name(name, new_socket):
        return []

    """
    CR (misha): 
        To prevent bugs a good rule of thumb is that a function either changes state or return value
        in this case the function return the requests by could also change the state of 2 globals 
            1. CLIENTS
            2. MESSAGES_TO_SEND
        
        what happens if some one would call this method just to read a name from the socket without changing globals 
        could he?
        
    """
    CLIENTS[name] = new_socket

    if name in ADMINS:
        name = ADMIN_SYMBOL + name
    if DEBUG:
        logging.info("New client {0}. \nip: {1}".format(name, new_socket.getpeername()[0]))

    """
    CR (misha): 
        This is another good example to wrap globals with a method, what will happen if each element in MESSAGES_TO_SEND
        will instead of being [name, message, and some other variable that is hard to understand]
        will have a message color as well?
        method like this         
        add_message_to_send(name, message, to_who):
        will become :
        add_message_to_send(name, message, to_who, color=colors.WHITE):
        
        and no other code would change. 
    """
    MESSAGES_TO_SEND.append(["server", "{} joined the chat. Yes, hrrrm.\n".format(name), False])  # server --> name


def valid_name(name, new_socket):
    if not name:
        return False

    if name in CLIENTS:
        MESSAGES_TO_SEND.append(["server", "Taken that username already is. Try another.\n", new_socket])
        return False

    """
    CR (misha): 
        Seems that the literal string "server" used in a few places in the code, consider making it a global, 
        or even better a function that will return the server name 
    """
    if name[0] == ADMIN_SYMBOL or name == "server":
        MESSAGES_TO_SEND.append(["server", "Illegal that username is. The dark side i sense in you.\n", new_socket])
        return False

    if name == MASTER_ADMIN[0] and new_socket.getpeername()[0] != MASTER_ADMIN[1]:
        MESSAGES_TO_SEND.append(["server", "Don't use the name of he who must not be named.\n", new_socket])
    return True


def get_request(sock):
    """
    CR (misha):
        There are few ways to fail a function
            1. returning different type then the output should be (None is a good way to handle this)
                1.1. But then You need to document this in the docstring ( you have none )
            2. Returning a tuple (bool, empty return) and then the bool indicates if this failed or not
                2.1. should be documented as well
            3. Throwing a built-in or custom exception
                3.1. should be documented as well

        Any way returning an empty string instead of a list is a bad idea
        ( what will happen if this method will change to return a string as a valid result, then empty string
        could be a valid result)

    BTW the global access to CLIENTS here as well ( just like in main )
    """
    if sock not in CLIENTS.values():
        request = get_name(sock)
        """
        CR (misha): Why not returning the request, this if is funny
        """
        if request == "":
            return request
        return []
    request = protocol.get_request(sock)
    return request


def valid_request(request, sock):
    if not request:
        return False
    name, command, data = request

    if name not in CLIENTS or CLIENTS[name] is not sock:
        return False

    if name in MUTED_CLIENTS:
        """
        CR (misha): 
            As i understand this method need to return true if the request is valid and false otherwise ( as there is
                no documentation at all i can just assume this)
            then if some one will call this function twice this will send the message twice ?! 
        """
        message = "Been muted you have. Messages in the chat you cant write!\n"
        MESSAGES_TO_SEND.append(("server", message, CLIENTS[name]))
        return False

    if command not in COMMANDS:
        return False

    if command in ADMIN_COMMANDS and name not in ADMINS:
        return False

    return True


def handle_request(request):
    name, command, data = request
    if command == "1" and data[0] in SPECIAL_MESSAGES.keys():
        special_request = data.pop(0)
        special_request = SPECIAL_MESSAGES[special_request]
        special_request(name, *data)
        return
    command = COMMANDS[command]
    command(name, *data)


def message_format(name, massage):
    if name in ADMINS:
        name = ADMIN_SYMBOL + name
    return "{0}: {1}\n".format(name, massage)


def send_waiting_messages(writeable_sockets):
    for message_block in MESSAGES_TO_SEND:
        """
        CR (misha): 
            WTF!!!!!!!!! are you seriously modify a list while iterating over it????????
            This is a huge problem!!!!!!!!!
            
            IN[1]: a = [1,2,3,4,5]
            IN[2]: for b in a:
              ...:     a.remove(b)
              ...:     print(b)
              ...:     
            OUT[2]:1
                   3
                   5
        """
        """
        CR (misha): I couldn't find easy documentation of how a message should look like
        """
        sender, message, recipient = message_block
        """
        CR (misha): here `formatted_message` should is a better name
        
        also dont use string cat, use format instead 
        """
        message = datetime.now().strftime("%H:%M:%S") + " " + message

        if recipient:
            if sender == "server":
                protocol.send_message(recipient, message)
                continue
            if recipient not in writeable_sockets:
                continue

            protocol.send_message(recipient, message)

            if PRINT_PRIVATE_MESSAGES:
                print_private_messages(recipient, message)
            """
            CR (misha):
                Should this continue be here?

                EDIT:
                Ohh fuck, reading the rest of the function made it clear
                this entire 'if' is for privet messages, consider making it an helper function
                (keep the continue
            """
            continue

        """
        CR (misha): Why is there a comma?
        """
        print message

        for sock in writeable_sockets:
            if sock == CLIENTS.get(sender):
                continue
            protocol.send_message(sock, message)
    global MESSAGES_TO_SEND
    MESSAGES_TO_SEND = []


def print_private_messages(recipient, message):
    recipient_name = "Unknown"
    """
    CR (misha): While some times a reverse-lookup is good here it seems that it is a result of a bad design
    """
    for name in CLIENTS:
        if CLIENTS[name] == recipient:
            """
            CR (misha): Why keep iterating if you found the name?
            """
            recipient_name = name
    print ("{0}, recipient: {1}".format(message, recipient_name)),


def delete_client(sock):
    """
    CR (misha):
        Classic example to ehy i hate global direct access to variables, what if some one iterates
        over OPEN_CLIENT_SOCKETS in this moment in other thread
    """
    OPEN_CLIENT_SOCKETS.remove(sock)
    sock.close()
    """
    CR (misha): Again CLIENTS here!
    """
    if sock not in CLIENTS.values():
        """
        CR (misha): Consider using logging instead of prints
        """
        logging.DEBUG("Unknown socket disconnected")
        return

    deleted_client_name = ""
    """
    CR (misha): 
        Could not understand what CLIENTS.keys are just from reading this code ( socket, names, objects... )
        dont use 'n' as a variable name 
    """
    for name in CLIENTS.keys():
        if CLIENTS[name] is sock:
            deleted_client_name = name
            del CLIENTS[name]

    """
    CR (misha): This is not the first time i read this snippet of code, it should be wrapped behind some logic
    """
    if deleted_client_name in ADMINS:
        name = ADMIN_SYMBOL + deleted_client_name
    MESSAGES_TO_SEND.append(["server", "Left the chat {} has!\n".format(deleted_client_name), False])

    """
    CR (misha): actually i like that you have this as an optional, good job ^^ 
    """
    if HARD_THROW:  # if HARD_THROW is on delete client from Admin and Mute lists
        """
        CR (misha): What is MASTER[0] name? socket? this code is unreadable 
        """
        if deleted_client_name in ADMINS and deleted_client_name != MASTER_ADMIN[0]:
            ADMINS.remove(deleted_client_name)

        if deleted_client_name in MUTED_CLIENTS:
            MUTED_CLIENTS.remove(deleted_client_name)

    logging.DEBUG("{} disconnected".format(deleted_client_name))


def main():
    """
    this is 12.6 chat server
    """
    """
    CR (misha): 
        Adding documentation is important but adding documentation every other line is a bit to much
        If you find yourself needing to do this then the code is not readable 
        In such case you have few options:
            * split to helper functions 
            * Think if the code could be better
    """
    logging.basicConfig(level=LOGGING_STATE)
    try:
        ip = sys.argv[1]
        port = int(sys.argv[2])
    except Exception, e:
        print e
        #logging.DEBUG(str(e))
        ip = SERVER[0]
        port = SERVER[1]
    server_is_up, server_socket = start_server(ip, port)  # function starts the server
    if not server_is_up:
        main()
        exit()
    """
    CR (misha):
        If i were to import youre code should i call main to start the server? 
        Have you seen a lib in the wiled that asks you to call its main???!!!  
    """
    while True:
        """
        CR (misha):
            Accessing globals directly has the benefits of a quick and dirty code 
            but if you would change the format of lets say CLIENTS to be of format 
            <name>: {
                socket: <socket>
                chat_room: <chat_id>
            }  
            You would need to change it in any place you have used CLIENTS
            but if this will be wrapped with a simple methd liek:
            def get_clients_socket() -> List[socket.socket]:
                return CLIENTS.values()
            you will only need to change this function.
        """
        readable_sockets, writeable_sockets, error_sockets = select.select(
            [server_socket] + OPEN_CLIENT_SOCKETS,
            CLIENTS.values(),
            OPEN_CLIENT_SOCKETS
        )

        if server_socket in readable_sockets:  # this section add sockets to OPEN_CLIENT_SOCKETS list
            get_new_client(server_socket)
            readable_sockets.remove(server_socket)

        """
        CR (misha):
            If you will have a method called handle_client ir something like this it will make the code more readable
            
            for current_socket in readable_sockets:
                handle_client(current_socket)
        """
        for current_socket in readable_sockets:
            # this section get requests from readable sockets, first request is user name
            handle_client(current_socket)

        send_waiting_messages(writeable_sockets)  # this command sends waiting messages
        for sock in error_sockets:  # this socket delete clients or sockets with socket errors
            delete_client(sock)



if __name__ == '__main__':
    main()
