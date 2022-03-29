'''
Console-based module for weather app server side functionality
'''
import threading
import datetime
import logging
import socket
import queue
import json
import sys
import os
from pathlib import Path
from enum import Enum

from weather_data_handler import WeatherDataHandler, WeatherDataModifier
from user_data_handler import UserDataHandler

D_HOST = '0.0.0.0'
D_PORT = 7878
D_BACKLOG = 1
MAX_CLIENTS = 5
FORMAT = 'utf-8'

HEADER_LENGTH = 8
ID_LENGTH = 4

isbundled = getattr(sys, 'frozen', False) and hasattr(sys,'_MEIPASS')

EXE_PATH = os.path.join(Path(__file__).parent.absolute() if not isbundled else os.path.dirname(sys.executable))

try:
    os.mkdir(os.path.join(EXE_PATH, "data"))
except:
    pass

WEATHER_DATA_PATH = os.path.join(EXE_PATH,"data\\weather_data.json")
USER_DATA_PATH = os.path.join(EXE_PATH,"data\\user_data.json")

LOG_PATH = os.path.join(EXE_PATH,"server.log")

#-------------------- Set-up for logger --------------------#
log = logging.getLogger(__name__)

f_formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s at %(lineno)d in %(funcName)s of %(filename)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
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
def threaded(func) -> threading.Thread:
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=False)
        thread.start()
        return thread
    return wrapper

def threaded_daemon(func) -> threading.Thread:
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    return wrapper


class MessagingHandler:
    '''
    Class for handling messages to a client and back via a socket.
    Its message takes the form of: [HEADER - 8 bytes][ID - 2 bytes] <Actual Message>
    Messages are sent ad-hoc with SendMessage method while received messages are put to an external queue (see ListenForRequests method)
    
    Static Attributes:
        UniversalRequestQueue (queue.Queue):
            A common Queue for all objects of the class to put received messages, if configured to
            Set up a Queue object prior to create any objects of this class if you plan to have a common request queue.
        ServerDisconnectionEvent (threading.Event):
            A common Event for all objects of the class for additional control from the server program
            Set up an Event object prior to create any objects of this class.
    Attributes:
        id (int):
            an id for external identification purposes
        socket (socket.socket):
            the communication socket, will be closed once the destructor is called
        replyQueue (queue.Queue):
            
    '''

    UniversalRequestQueue = None
    ServerDisconnectionEvent = None

    @staticmethod
    def Reset():
        '''
        Reset class attributes to None
        Only call this method after all objects of this class has been destroyed or handled properly
        '''
        MessagingHandler.UniversalRequestQueue = None
        MessagingHandler.ServerDisconnectionEvent = None

    def __init__(self, id:int, clientSocket:socket.socket, addr):
        '''
        Constructor for MessagingHandler object
        Parameters:
            id (int): 
                an id assigned by the server program for identification purposes
                The constructor is not responsible of ensuring the id is unique
            socket (socket.socket):
                The communication socket returned by a call to serverSocket.accept beforehand
                Upon destroying the object this socket will automatically be closed
            address (str):
                The address of the socket returned with a call to serverSocket.accept beforehand
            clientDisconnectionEvent (threading.Event):
                An event, flagged when the client wants to disconnect
        '''
        self.id = id
        self.socket = clientSocket
        self.address = addr
        self.logged_in = False
        log.info(f'New messaging handler with id {id} for {self.address}')

    def __del__(self):
        pass

    def SetLoggedIn(self, username):
        self.logged_in = True
        self.username = username

    def SendMessage(self, message:bytes, id:int):
        '''
        Send a message to client
        
        Parameters:
            message (bytes):
                A message in bytes
            id (int):
                client-specific identifier of the request, a reply has the same id as the request it answers to
        Returns:
            status (bool):
                True if the message is sent without any server side or connection issues
                False if any errors occured, and logs traceback in module level's log file
        '''
        bytes_sent = 0
        length = 0
        try:
            length = len(message) + HEADER_LENGTH + ID_LENGTH
            assert length <= 0xFFFFFFFFFFFFFFFF
            header = length.to_bytes(HEADER_LENGTH, byteorder='big')
            reqID = id.to_bytes(ID_LENGTH, byteorder='big')
            message = b''.join([header, reqID, message])
        
            bytes_sent = self.socket.send(message)
            assert bytes_sent == length, "Length of message sent does not match that of the actual message"

            log.info(f"Sent message of length {length} to client {self.id} at {self.address}")
            return True
        except AssertionError as e:
            log.info(f"Couldn't send full message of length {length} to client {self.id} at {self.address}. Only {bytes_sent}")
        except Exception as e:
            log.exception(f"Counld not send message of length {length} to client {self.id} at {self.address}.")

        return False
    
    @threaded
    def ListenForRequests(self, requestQueue:queue.Queue=None):
        '''
        Threaded - Enable message listening mechanism for a handler
        The method actively listens for requests
        The method terminates if:
            - The connection is lost
            - The server wants to disconnect, this will only happens once the client confirms with a specific message
            - the client wants to disconnect (via a message), this will happens once a specific message is received, regardless of unsent replies
        Parameters:
            requestQueue (queue.Queue):
                The queue for requests to be put in for processing
                Default is None.
                If None, this object will use the class level UniversalRequestQueue to put in requests
        '''
        reqQueue = requestQueue if requestQueue else MessagingHandler.UniversalRequestQueue
        log.info(f"Client {self.id} has started listening for requests")
        while True:
            message = None
            reqID = None
            try:
                # Listens for HEADER message
                header_of_message = self.socket.recv(HEADER_LENGTH, socket.MSG_PEEK)
                if header_of_message:
                    message_length = int.from_bytes(header_of_message, byteorder='big')
                    if message_length:
                        bytesReceived = 0
                        chunks = []
                        while bytesReceived < message_length:
                            message = self.socket.recv(message_length - bytesReceived)
                            bytesReceived += len(message)
                            chunks.append(message)
                        message = b''.join(chunks)
                        # message is now b'<HEADER><ID><MESSAGE>'
                        reqID = int.from_bytes(message[HEADER_LENGTH:HEADER_LENGTH + ID_LENGTH], byteorder='big')
                        message = message[HEADER_LENGTH + ID_LENGTH:]
                        log.info(f"Client handler {self.id} has received message of length {message_length}")
            except ConnectionResetError as e:
                # This thread should now close
                reqQueue.put((self.id, id, b'DISCONNECT'))
                log.info(f"Abrupt disconnection occured while listening for client {self.id}'s requests. The connection will effectively close")
                break
            except Exception as e:
                # Please handle errors
                log.exception(f"Exception occured on client {self.id}'s listening thread")

            # Now that we have a request
            if message:
                # 1. If the request is "CONFIRM DISCONNECTION" AND server_disconnect Event is set
                #   It means the server has previously sent a request to disconnect and client has confirm disconnection
                #   -> Break
                if MessagingHandler.ServerDisconnectionEvent.is_set() and message == b'CONFIRM DISCONNECTION':
                    log.info(f"Client {self.id} at {self.address} has confirmed disconnection for server.")
                    break

                # 2. If the request is "DISCONNECT"
                #   It means the client wants to and will disconnect
                #   -> Break, set client_disconnect Event
                # Maybe?
                elif message == b'DISCONNECT':
                    log.info(f"Client {self.id} at {self.address} has queued for disconnection.")
                    reqQueue.put((self.id, reqID, message))
                    break

                # 3. Any other messages: Pass it down to UniversalRequestQueue
                reqQueue.put((self.id, reqID, message))
                log.info(f"Client handler {self.id} has posted of length {message_length} to the process queue")
                
            # Go back to listening

        log.info(f"Client {self.id} handler's listener thread for {self.address} has terminated")


class ServerProgram:
    '''
    Base class for server side weather app program
    Provides a compact interface to open server and handle clients' requests
    without additional controls
    Attributes:
        maxClients (int):
            indicates the number of client sockets a class' object can handle at once
        serverSocket (socket.socket):
            the socket object for the listening server
        clients (list):
            a list of tuples in form of (handlerThread, clientSocket, address). DO NOT access directly:
            - handlerThread (threading.Thread): the thread handling a single client's requests
            - clientSocket (socket.socket): the socket object for communicating a client
            - address (str): address of the client connecting to the socket
        weatherDataHandler:
            a WeatherDataHandler object, used to fetch weather data queries
        userdataHandler:
            a UserDataHandler object, used for logins and registerations.
        adminWeatherHandler:
            a WeatherDataModifier object, used for an admin to modify the weather data
        universalRequestQueue (queue.Queue):
            a request queue (id, request) for structured requests from clients
        serverDisconnectionEvent (threading.Event):
            an event signals a top-level disconnection of all clients' channels
    '''

    def __init__(self):
        '''
        Constructor for ServerProgram object, creates a ServerProgramObject without opening the server
        Parameters:
            maxclient (int): maximum amount of clients allow to connect to the server
        
        Raises:
            RuntimeError: raised when the underlying weather or user databases is inaccessible or lacking.
        '''
        self.started = False
        self.editing = False
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.weatherDataHandler = WeatherDataHandler(WEATHER_DATA_PATH)
        self.userDataHandler = UserDataHandler(USER_DATA_PATH)
        self.adminWeatherHandler = None
        self.universalRequestQueue = queue.Queue()

        self.clientListLock = threading.Lock()
        self.weatherDatabaseLock = threading.Lock()
        self.serverDisconnectionEvent = threading.Event()

        MessagingHandler.UniversalRequestQueue = self.universalRequestQueue
        MessagingHandler.ServerDisconnectionEvent = self.serverDisconnectionEvent

        log.info(f"Server program created.")

    def __del__(self):
        pass
    
    def Run(self):
        '''
        Depricated
        Console-based method to run the server object, mostly for debugging purposes
        '''
        # host = input("Host: ")
        # port = int(input("Port: "))
        # backlog = int(input("Backlog: "))
        # connectionThread = self.OpenServer(host, port, backlog)
        connectionThread = self.OpenServer()
        log.info(f"Opened new thread {connectionThread} to handle server's connection requests")

        processthread = self.ProcessRequestQueue()
        log.info(f"Opened new thread {processthread} to handle clients' requests")

        a = input("Terminate by any input: ")
        self.serverDisconnectionEvent.set()
        self.serverSocket.close()
        log.info(f"Server has issued disconnection to all clients")

        for connection in self.clients:
            if connection != (None, None):
                connection[1].SendMessage(b'DISCONNECT', 0xFFFF)
                connection[0].join()

        connectionThread.join()
        processthread.join()
        log.info(f"All client handlers has terminated")

    def Initiate(self):
        self.userDataHandler.LoadDatabase()
        self.weatherDataHandler.LoadDatabase()

    def Cleanup(self):
        self.userDataHandler.SaveDatabase()

    def Start(self, host=D_HOST, port=D_PORT, backlog=D_BACKLOG, num_clients=5):
        '''
        Callback to start the program
        '''
        if self.started:
            return

        self.serverDisconnectionEvent.clear()
        self.maxClients = num_clients
        self.clients = [(None, None) for _ in range(self.maxClients)]
        self.connectionThread = self.OpenServer(host, port, backlog)
        log.info(f"Opened new thread {self.connectionThread} to handle server's connection requests")

        self.processthread = self.ProcessRequestQueue()
        log.info(f"Opened new thread {self.processthread} to handle clients' requests")
        self.started = True

    def End(self):
        '''
        Callback to close server and end program
        '''
        if not self.started:
            return
            
        self.serverDisconnectionEvent.set()
        self.serverSocket.close()
        self.serverSocket = None
        log.info(f"Server has issued disconnection to all clients")

        for connection in self.clients:
            if connection != (None, None):
                connection[1].SendMessage(b'DISCONNECT', 0xFFFF)
                connection[0].join()

        if self.connectionThread:
            self.connectionThread.join()
        if self.processthread:
            self.processthread.join()
        self.connectionThread = None
        self.processthread = None
        log.info(f"All client handlers has terminated")
        self.started = False

    def EnterEditMode(self):
        '''
        Start edit mode.
        It is advisable to disconnect (using End method) from all clients before entering edit mode
        Edit mode allows an admin to edit the weather database using the returned WeatherDataModifier
        Clients can still connects to and fetch data using the old database
        Returns:
            adminWeatherHandler (WeatherDataModifier)
        '''
        if not self.editing:
            self.adminWeatherHandler = WeatherDataModifier(WEATHER_DATA_PATH)
            self.adminWeatherHandler.LoadDatabase()
            self.editing = True
            
        return self.adminWeatherHandler

    def ExitEditModeAndReload(self, save=True):
        '''
        End edit mode and reloads the database
        Parameters:
            save (bool):
                Dictates whether edits are saved or not
        '''
        if self.editing: 
            if save:
                self.adminWeatherHandler.SaveDatabase()

            self.adminWeatherHandler = None
            
            with self.weatherDatabaseLock:
                self.weatherDataHandler.LoadDatabase()

            self.editing = False

    def IsWeatherDataChangedSinceLoaded(self):
        '''
        Queries whether the weather database has received a change since the last time it's loaded in edit mode

        Returns:
            status (bool):
                True if at least one meaningful change is made
                False if the program is not in edit mode, or no changes has been made
        '''
        return self.adminWeatherHandler and self.adminWeatherHandler.changed
        
    @threaded_daemon
    def OpenServer(self, host=D_HOST, port=D_PORT, backlog=D_BACKLOG):
        '''
        Threaded (daemon) - Open the server at (host, port) for backlog ammount of unaccepted connections
        
        Parameters:
            host (str): host part
            port (int): port
            backlog (int): backlog number
        '''
        #Obligatory binding and listen


        log.info(f"Server socket opened at ({host}, {port}) for {self.maxClients} clients")
        while True:
            if self.serverDisconnectionEvent.is_set():
                break

            while self.clients.count((None, None)) > 0:
                if not self.serverSocket:
                    self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.serverSocket.bind((host, port))
                    self.serverSocket.listen(backlog)

                try:
                    clientSocket, address = self.serverSocket.accept()
                except:
                    break

                with self.clientListLock:
                    for i in range(len(self.clients)):
                        if self.clients[i] == (None, None):
                            handler = MessagingHandler(i, clientSocket, address)
                            thread = handler.ListenForRequests()
                            log.info(f"{address} connected. Opened new thread {thread} to listen to their requests")

                            self.clients[i] = (thread, handler)
                            break

                log.info(f"Server program has opened {self.maxClients - self.clients.count((None, None))} sockets. {self.clients.count((None, None))} remaining")
            
            if self.serverSocket:
                self.serverSocket.close()
                self.serverSocket = None

        # Wait how do we stop connections if accept() just... blocks?
        log.info(f"Server connection thread has terminated")
        if self.serverSocket:
            self.serverSocket.close()
            self.serverSocket = None

    @threaded
    def ProcessRequestQueue(self):
        '''
        Threaded - Enable the universalRequestQueue to be processes
        After a request in the queue is process, the reply will be sent back to the client immediately
        '''
        while True:
            while not self.universalRequestQueue.empty():
                id, reqID, request = self.universalRequestQueue.get()
                reply = self.ProcessRequest(id, request)
                if reply and self.clients[id][0].is_alive():
                    log.info(f"Letting client {id}'s handler replying to their client. Reply is {reply}")
                    self.clients[id][1].SendMessage(reply, reqID)
                elif not reply:
                    self.clients[id] = (None, None)
                    log.info(f"Removed client {id}'s handler from client list")

            # Now that there are no more requests:
            if self.serverDisconnectionEvent.is_set():
                break

        log.info(f"Processing thread has terminated")

    def ProcessRequest(self, id:int, request:bytes):
        '''
        Determines appropriate actions for a request from client.
        Full list of all possible requests see .........
        A disconnection request will results in a hang for the client handler's listening thread to fully terminate before continuing
        Parameters:
            id (ind):
                id of the client, dictated by the program
            request (str):
                a request in string form
        
        Returns:
            reply (bytes):
                A status code and extra data (if any) produced after processing, needed to send back to client
            
        Raises:
            eh?
        '''
        log.info(f"Now processing Client {id}'s request: {request}")
        status = b'INVALID'
        reply = None
        if request == b'DISCONNECT':
            with self.clientListLock:
                self.clients[id][0].join()

            return None
        else:
            cmd, param = ServerProgram.SplitOnce(request)
            if cmd and param:
                if cmd == b'LOGIN':
                    param = param.decode(FORMAT)
                    username, password = ServerProgram.SplitOnce(param)
                    
                    loginstatus = self.userDataHandler.Verify(username, password)
                    if loginstatus == UserDataHandler.LoginState.VALID:
                        status = b'SUCCEEDED'
                        self.clients[id][1].SetLoggedIn(username)
                    else:
                        status = b'FAILED'
                        if loginstatus == UserDataHandler.LoginState.NO_USERNAME:
                            reply = b'USERNAME NOT FOUND'
                        elif loginstatus == UserDataHandler.LoginState.WRONG_PASSWORD:
                            reply = b'WRONG PASSWORD'
                elif cmd == b'REGISTER':
                    param = param.decode(FORMAT)
                    username, password = ServerProgram.SplitOnce(param)
                    registerstatus = self.userDataHandler.Register(username, password)
                    if registerstatus == UserDataHandler.RegisterState.VALID:
                        status = b'SUCCEEDED'
                    else:
                        status = status = b'FAILED'
                        if registerstatus == UserDataHandler.RegisterState.DUPLICATE:
                            reply = b'USERNAME ALREADY EXISTS'
                else:
                    if self.clients[id][1].logged_in:
                        if cmd == b'WEATHER':
                            mode, param = ServerProgram.SplitOnce(param, errorOnNoTrail=False)
                            if mode == b'ALL':
                                date = None
                                validDate = True
                                if param:
                                    try:
                                        date = datetime.datetime.strptime(param.decode(FORMAT), '%Y/%m/%d').date()  
                                    except Exception as e:
                                        validDate = False
                                        status = b'FAILED'
                                        reply = b'WRONG DATE FORMAT'
                                else:
                                    date = datetime.date.today()

                                if validDate:
                                    alist = None
                                    with self.weatherDatabaseLock:
                                        alist = self.weatherDataHandler.FetchAllCitiesByDate(date)
                                    reply = json.dumps(alist).encode(FORMAT)
                                    status = b'SUCCEEDED'
                                
                            elif mode == b'RECENT':
                                city_id, count = ServerProgram.SplitOnce(param, errorOnNoTrail=False)
                                good_values = True
                                try:
                                    city_id = int(city_id.decode(FORMAT))
                                    count = 7 if not count else int(count.decode(FORMAT))
                                except:
                                    status = b'FAILED'
                                    reply = b'VALUE ERROR'
                                    good_values = False

                                if good_values:
                                    fetchstate = False
                                    res = None
                                    with self.weatherDatabaseLock:
                                        fetchstate, res = self.weatherDataHandler.FetchForcastsByCity(city_id, datetime.date.today(), count)
                                    status = b'SUCCEEDED' if fetchstate else b'FAILED'
                                    reply = json.dumps(res).encode(FORMAT) if fetchstate else b'NO CITYID'
                    else:
                        status = b'FAILED'
                        reply = b'NOT LOGGED IN'

        log.info(f"Done processing Client {id}'s request: {request}")
        return status + b' ' + reply if reply else status

    @staticmethod
    def SplitOnce(request, errorOnNoTrail=True):
        '''
        '''
        splitted = None
        try:
            if type(request) == bytes:
                splitted = request.split(b' ', 1)
            if type(request) == str:
                splitted = request.split(' ', 1)
            assert splitted and len(splitted) == 2, "Request is missing additional parameters"
            return splitted[0], splitted[1]
        except AssertionError:
            if not errorOnNoTrail:
                return splitted[0], None
    
            return None, None

if __name__ == '__main__':
    a = ServerProgram()
    a.Start()
    m = input()
    a.End()
    pass