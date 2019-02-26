'''
    file:   RFCServer.py
    author: Daniel Mills (demills)

    Implementation of a multithreaded server that provides two services. 

       1) RFCQuery : A peer requests this peer's current RFC index. 
       2) GetRFC   : A peer requests to download a specific RFC document from this peer.

    The RFCServer should be instantiated by the RFCClient before a peer registers
    with the RegistrationServer.

'''

import socket
import threading
import time
import signal, os

'''
    Class for threads spawned by the server to handle communication with
    another peer.

'''
class PeerThread(threading.Thread) : 
    def __init__( self, ip_addr, port, socket ):
        threading.Thread.__init__(self)
        self.ip_addr = ip_addr
        self.port = port
        self.socket = socket

    def run( self ) :
        request_bytes = self.socket.recv( 2048 )

        # convert the request in bytes to string
        request = str( request_bytes.decode('ascii') )

        print(request)

        # obtains the method of this protocol
        method = request.splitlines()[0]

        if method == "RFCQuery" :
            print ( "TODO" )
            
        elif method == "GetRFC" :
            print ( "TODO" )

'''
'''
class RFCServer() :
    ''' 
        Initializes the RFCServer:
            - Creates and binds a socket to listen for incoming peers.
            - Sends the client the port chosen to listen on.
            - Instantiates instance variables:
                rfc_index: Initial RFCIndex passed from ClientPeer.
                serv_sock: Socket the server listens for peers on.
                serv_pipe: Pipe for communication with ClientPeer.
                serv_port: Port number the server is listening on.
        Then, starts the main server function "runServer()". The server will
        remain in this function until PeerClient sends a SIGTERM from PeerClient.
        
    '''
    def __init__( self, serv_pipe, rfc_index ) :
        # Initializes the RFC index.
        self.rfc_index = rfc_index

        # Creates socket to listen for incoming peers on.
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Gets this computer's IP address which the socket will listen on.
        ip_addr = self.getIPAddress() 

        # Binds socket to a random, available port. 
        self.serv_sock.bind( (ip_addr, 0) )

        # Gets the port number "serv_sock" is bound to ...
        self.serv_port = self.serv_sock.getsockname()[1]

        # ... and sends it back to the Client.
        self.serv_pipe = serv_pipe
        self.serv_pipe.send( self.serv_port )
    
        print( "RFCServer: %s\n" %os.getpid() )

    '''
        Returns this computer's IP address. 
    '''
    def getIPAddress( self ) :
        # Creates socket to Google's nameserver.
        sock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        sock.connect(( "8.8.8.8", 80 ))

        # Gets this computer's IP address from the socket connection.
        ip_addr = sock.getsockname()[0]

        sock.close()
        return ip_addr

    def killServer( self ) :
        self.serv_sock.close()

    def run( self ) :
        i = 0
        while True :
            try :
                time.sleep(2)
                i += 2
            except KeyboardInterrupt :
                time.sleep(3)
                break
