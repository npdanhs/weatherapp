'''
Console-based module for weather app client side functionality
'''
import datetime
import threading
import logging
import socket
import queue
import json
import time
import sys
import os
from pathlib import Path
from enum import Enum

D_HOST = '127.0.0.1'
D_PORT = 7878
FORMAT = 'utf-8'

HEADER_LENGTH = 8
ID_LENGTH = 4

isbundled = getattr(sys, 'frozen', False) and hasattr(sys,'_MEIPASS')

LOG_PATH = os.path.join(Path(__file__).parent.absolute() if not isbundled else os.path.dirname(sys.executable), "client.log")

#-------------------- Set-up for logger --------------------#
log = logging.getLogger(__name__)

f_formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s at %(funcName)s in %(filename)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
c_formatter = logging.Formatter(fmt="[%(levelname)s] %(message)s", datefmt="")

f_handler = logging.FileHandler(filename=LOG_PATH, mode='w+')
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(f_formatter)

# c_handler = logging.StreamHandler()
# c_handler.setLevel(logging.WARNING)
# c_handler.setFormatter(c_formatter)

log.setLevel(logging.DEBUG)
log.addHandler(f_handler)
# log.addHandler(c_handler)

#-------------------- Threaded decorator --------------------#
def threaded(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper

def threaded_daemon(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    return wrapper

class ClientProgram:
    '''
    Class for the client program that represents and encapsulates traffic and commands to and from a server for weather data
    Attributes:
        sock (socket.socket):
            The communication socket with the server
        connected (bool):
            indicates the status of the communication channel
        requestID (int):
            current requestID for this connection session
        dataQueue (queue.Queue):
            Queue for replies from the server
        
    '''
    class State(Enum):
        '''
        Provides an enumeration for standard communicative status between client and servers.
        All request wrapper should return a State status
        - SUCCEEDED: the request is sent perfectly and there might be extra data attached from the server
        - FAILED: the request is sent perfectly but the server did not process successfully
        - BADCONNECTION: the request is not sent
        - BADMESSAGE: the reply from server is faulty
        - INVALID: the request is flagged as invalid by the server
        '''
        SUCCEEDED = 1,
        FAILED = 2,
        INVALID = 3,
        BADCONNECTION = 4,
        BADMESSAGE = 5

    States = {  b'SUCCEEDED' : State.SUCCEEDED,
                b'FAILED' : State.FAILED,
                b'INVALID' : State.INVALID }

    def __init__(self):
        '''
        Constructs a client program object
        '''
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.requestID = 0
        self.replies= dict()

        self.disconnectEvent = threading.Event()
        log.info("Client program initiated")
        pass

    def Connect(self, host=D_HOST, port=D_PORT):
        try:
            if not self.sock:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.requestID = 0
            log.info(f"Connected to server at ({host}, {port})")
            self.listenThread = self.ListenForMessages()
            self.connected = True
            return True
        except Exception as e:
            log.exception("Exception occured. No connection established.")
            return False

    def Disconnect(self):
        if not self.connected:
            return
            
        self.sock.close()
        if self.listenThread:
            self.listenThread.join()
        self.sock = None
        log.info("Socket closed. Connection to server has terminated")
        self.connected = False

    def Run(self):
        listenThread = self.ListenForMessages()

        while True:
            if self.disconnectEvent.is_set():
                break

            req = input("Request: ")
            self.SendMessage(req.encode(FORMAT))
            if req == 'DISCONNECT':
                self.disconnectEvent.set()

            data = None
            
            while True:
                if self.disconnectEvent.is_set():
                    break
                if not self.dataQueue.empty():
                    data = self.dataQueue.get()
                    self.requestID += 1
                    break

            print(data)
            
        self.Disconnect()
        listenThread.join()
        print("Client program ended")

    def GetReplyFor(self, id, timeout=None):
        '''
        Returns reply for a request with id in timeout seconds.
        Parameters:
            id (int)
            timeout (float | None): default is None
                time to wait for reply.
                if None, waits indefinitely.
                Recommended to supply a timeout
        Returns:
            message (bytes | None)
                any message that came through
                None is never returned if timeout is also None
        '''
        totalTime = 0.0
        while True:
            if id not in self.replies:
                time.sleep(0.1)
                totalTime += 0.1
                if timeout and totalTime > timeout:
                    return None
            else:
                popped = self.replies.pop(id)
                return popped
                
    def Login(self, username:str, password:str):
        '''
        Wrapper function to request to the server command 'LOGIN'
        Parameters:
            username (str): self-explanatory
            password (str): self-explanatory
        Returns:
            state (ClientProgram.State):
                dictates the status of the request
            errorMessage (string | None):
                an attached error message from server, if any, indicates the problem with the requested login
        '''
        message = ' '.join(['LOGIN', username, password])
        state, id = self.SendMessage(message.encode(FORMAT))
        if state:
            reply = self.GetReplyFor(id, timeout=3)
            try:
                if reply:
                    state, error = ClientProgram.SplitOnce(reply)
                    return ClientProgram.States[state], error.decode(FORMAT) if error else None
            except:
                return ClientProgram.State.BADMESSAGE, None
        
        return ClientProgram.State.BADCONNECTION, None

    def Register(self, username:str, password:str):
        '''
        Wrapper function to request to the server command 'REGISTER'
        Parameters:
            username (str): self-explanatory
            password (str): self-explanatory
        Returns:
            state (ClientProgram.State):
                dictates the status of the request
            extraData (bytes):
                an attached error message from server, if any, indicates the problem with the requested registration
        '''
        message = ' '.join(['REGISTER', username, password])
        state, id = self.SendMessage(message.encode(FORMAT))
        if state:
            reply = self.GetReplyFor(id, timeout=3)
            try:
                if reply:
                    state, error = ClientProgram.SplitOnce(reply)
                    return ClientProgram.States[state], error.decode(FORMAT) if error else None
            except:
                return ClientProgram.State.BADMESSAGE, None
        
        return ClientProgram.State.BADCONNECTION, None

    def RequestWeatherDataAll(self, date:str=None):
        '''
        Wrapper function to request to the server command 'LISTALL'
        Parameters:
            date (datetime.date | None): default is None
                date to query the weathers, if None is passed, request for today's
        Returns:
            state (ClientProgram.State):
                dictates the status of the request
            data (list):
                a list of lists in form of [city_id, city_name, weather, temperature, humidity, wind_speed]
        '''
        date = date if date else datetime.date.today().strftime('%Y/%m/%d')
        
        message = ' '.join(['WEATHER ALL', date])
        state, id = self.SendMessage(message.encode(FORMAT))
        if state:
            reply = self.GetReplyFor(id, timeout=3)
            try:
                if reply:
                    state, data = ClientProgram.SplitOnce(reply)
                    if state == b'SUCCEEDED':
                        data = json.loads(data)
                    return ClientProgram.States[state], data
            except:
                return ClientProgram.State.BADMESSAGE, None
                    
        return ClientProgram.State.BADCONNECTION, None

    def RequestWeatherDate7DaysOf(self, city_id):
        '''
        Wrapper function to request to the server command 'LIST'
        Parameters:
        Returns:
            state (ClientProgram.State):
                dictates the status of the request
            data (list):
                A list of [city_name, weathers]
                weathers is a dictionary with 7 keys of string types, formatted 'YYYY/MM/DD'
                    Each element is a list in form of [weather, temperature, humidity, wind_speed]
        '''
        message = ' '.join(['WEATHER RECENT', str(city_id)])
        state, id = self.SendMessage(message.encode(FORMAT))
        if state:
            reply = self.GetReplyFor(id, timeout=3)
            try:
                if reply:
                    state, data = ClientProgram.SplitOnce(reply)
                    if state == b'SUCCEEDED':
                        data = json.loads(data)
                    return ClientProgram.States[state], data
            except:
                return ClientProgram.State.BADMESSAGE, None
                    
        return ClientProgram.State.BADCONNECTION, None

    def SendMessage(self, message:bytes):
        '''
        Send a message to the server
        
        Parameters:
            message (bytes):
                Message to send, in bytes
        Returns:
            state (bool):
                if True, the message is sent successfully
                if False, an error has occured and the message is either not sent or sent errorneously
            requestID (int)
        '''
        bytes_sent = 0
        try:
            length = len(message) + HEADER_LENGTH + ID_LENGTH
            assert length <= 0xFFFFFFFFFFFFFFFF
            header = length.to_bytes(HEADER_LENGTH, byteorder='big')
            reqID = self.requestID.to_bytes(ID_LENGTH, byteorder='big')
            message = b''.join([header, reqID, message])
        
            bytes_sent = self.sock.send(message)
            assert bytes_sent == length, "Length of message sent does not match that of the actual message"

            log.info(f"Sent message of length {length} to server.")
            return True, self.requestID
        except AssertionError as e:
            log.info(f"Couldn't send full message of length {length} to server. Only {bytes_sent}")
        except Exception as e:
            log.exception(f"Could not send message of length {length} to server.")

        return False, -1
    
    @threaded
    def ListenForMessages(self):
        '''
        Threaded - Enable message listening mechanism
        The method actively listens for requests
        The method terminates if:
            - The connection is lost
            - The server wants to disconnect, this will only happens once the client confirms with a specific message
            - the client wants to disconnect (via a message), this will happens once a specific message is received, regardless of unsent replies
        '''
        while True:
            message = None
            try:
                # Listens for HEADER message
                header_of_message = self.sock.recv(HEADER_LENGTH, socket.MSG_PEEK)
                if header_of_message:
                    message_length = int.from_bytes(header_of_message, byteorder='big')
                    if message_length:
                        bytesReceived = 0
                        chunks = []
                        while bytesReceived < message_length:
                            message = self.sock.recv(message_length - bytesReceived)
                            bytesReceived += len(message)
                            chunks.append(message)
                        message = b''.join(chunks)
                        # message is now b'<HEADER><ID><MESSAGE>'
                        reqID = int.from_bytes(message[HEADER_LENGTH:HEADER_LENGTH + ID_LENGTH], byteorder='big')
                        message = message[HEADER_LENGTH + ID_LENGTH:]
                        log.info(f"Client has received message of length {message_length}")
            except ConnectionResetError as e:
                self.disconnectEvent.set()
                log.info(f"Abrupt disconnection occured while listening for messages. The connection will effectively close")
                break
            except Exception as e:
                # Please handle errors, maybe?
                self.disconnectEvent.set()
                log.exception(f"Exception occured on listening thread.")
                break

            # Now that we have a message
            # If the message is "DISCONNECT"
            #   It means the server wants to disconnect
            #   -> Send confirm disconnection and break
            if message == b'DISCONNECT':
                log.info(f"Server has requested disconnection.")
                self.disconnectEvent.set()
                self.SendMessage(b'CONFIRM DISCONNECTION')
                break

            # Any other messages:
            self.replies[reqID] = message
            log.info(f'Reply received: {reqID}, {message}. {self.replies}')

        log.info(f"Listener thread has terminated")

    @staticmethod
    def SplitOnce(reply):
        '''
        '''
        try:
            if type(reply) == bytes:
                splitted = reply.split(b' ', 1)
            if type(reply) == str:
                splitted = reply.split(' ', 1)
            if len(splitted) == 2:
                return splitted[0], splitted[1]
            elif len(splitted) == 1:
                return splitted[0], None
        except:
            pass

        return None, None

if __name__ == '__main__':
    a = ClientProgram()
    a.Connect()
    while True:
        printthis1 = None
        printthis2 = None
        m = int(input("Choice: "))
        if m == 1:
            printthis1, printthis2 = a.Login('A', 'B')
        elif m == 2:
            printthis1, printthis2 = a.Register('A','B')
        elif m == 3:
            printthis1, printthis2 = a.RequestWeatherDataAll()
        elif m == 4:
            printthis1, printthis2 = a.RequestWeatherDate7DaysOf(32248)
        elif m == 5:
            a.Disconnect()
            break

        a.requestID += 1

        print(printthis1, printthis2)