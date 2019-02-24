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

class RFCServer() :
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

    ''' 
        Initializes the RFCServer:
            - Creates and binds a socket to listen for incoming peers.
            - Sends the client the port chosen to listen on.
    '''
    def __init__( self, server_pipe, rfc_index ) :
        # Creates socket to listen for incoming peers on.
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Gets this computer's IP address which the socket will listen on.
        ip_addr = self.getIPAddress() 

        # Binds socket to a random, available port. 
        self.serv_sock.bind( (ip_addr, 0) )

        # Gets the port number bound to and sends it back to the client.
        self.serv_port = self.serv_sock.getsockname()[1]
        server_pipe.send( self.serv_port )

    def killServer( self ) :
        self.serv_sock.close()
        
