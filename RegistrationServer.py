#!/usr/bin/env python3

from PeerList import PeerList
import ProtocolTranslator
import socket
import threading
import time
import sys
import PeerUtils


"""
A thread that handles the tcp connection between a single Peer
and the Registration Server.
"""
class PeerThread(threading.Thread):
    
    """
    Constructor for this tcp connection with the peer.
    Sets the ip address, port number, and socket for 
    this tcp connection.
    """
    def __init__( self, ip_addr, port, socket ):
        threading.Thread.__init__(self)
        self.ip_addr = ip_addr
        self.port = port
        self.socket = socket
        
    """
    Handles the request protocl sent from the peer and
    sends back the approriate response protocol to this
    peer over this tcp connection.
    """
    def run(self):
        try:
            # bytes sent from the peer
            request_bytes = self.socket.recv(2048)
            
            # convert the request in bytes to string
            request = str( request_bytes.decode('ascii') )

            # obtains the method of this protocol
            method = request.splitlines()[0]
    
            # Peer sends the Register request
            if method == "Register":
                # obtains the host, port, and cookie from the register request protocol
                host, port, c = ProtocolTranslator.registerQueryToElements( request )

                # acquire lock on the peer list before modifying
                lock.acquire()
                
                # registers this host in the peer list and obtains the cookie
                cookie = peer_list.register( host, port, c )

                # release lock on the peer list after modifying
                lock.release()
                
                # sends back a response message with the cookie
                response = ProtocolTranslator.registerResponseToProtocol( cookie )

                print(response)

                # translates the response protocol into bytes
                response_bytes = response.encode('ascii')
                
                # sends the response to the peer client
                self.socket.sendall( response_bytes )
                
            # Peer sends the Leave request  
            elif method == "Leave":
                
                # obtains the cookie for this peer from the request
                cookie = ProtocolTranslator.leaveQueryToElements( request )
                
                # acquires lock on the peer list before modifying
                lock.acquire()
                
                # attempts to have the peer leave if there is matching peer in the peerlist with this cookie
                # returns a boolean value of whether the peer successfully could leave
                peer_left = peer_list.leave( cookie )
                
                # releases lock on the peer list after modifying
                lock.release()
                
                # creates the protocol response to be sent back to the peer
                response = ProtocolTranslator.leaveResponseToProtocol( peer_left )
                
                print(response)
                
                # translates the response protocol into bytes
                response_bytes = response.encode('ascii')
                
                # sends the response to the peer client
                self.socket.sendall( response_bytes )

            # Peer sends the PQuery request
            elif method == "PQuery":

                # obtains the cookie for this peer from the request
                cookie = ProtocolTranslator.pqueryQueryToElements( request )
                
                # acquires lock on the peer list before modifying
                lock.acquire()
                
                # attempts to find the matching peer in this peer list based on the cookie
                # returns the peerlist of active peers or None if the peer hasn't registered yet
                p_list, status = peer_list.pQuery( cookie )
                                
                # releases lock on the peer list after modifying
                lock.release()

                p_list_str = ''
                if status == 1:
                    p_list = PeerList(p_list)
                    p_list_str = str(p_list)
     
                response = ProtocolTranslator.pqueryResponseToProtocol(status, p_list_str )
                
                print(response)
     
                # translates the response protocol into bytes
                response_bytes = response.encode('ascii')
                
                self.socket.sendall( response_bytes )
                    
            # Peer sends the KeepAlive request
            elif method == "KeepAlive":
                
                # obtains the cookie for this peer from the request
                cookie = ProtocolTranslator.keepAliveQueryToElements( request )
                
                # acquires lock on the peer list before modifying
                lock.acquire()
                
                # attempts to find the matching peer in this peer list based on the cookie
                # returns the a status code value if this was successful
                status_code = peer_list.keepAlive( cookie )
                
                # releases lock on the peer list after modifying
                lock.release()
                
                # sets boolean value of whether this peer could keepAlive to false
                can_keep_alive = False

                # if the keepAlive request was valid - set the boolean value to true
                if status_code == 1:
                    can_keep_alive = True
                
                # creates the protocol response to be sent back to the peer
                response = ProtocolTranslator.keepAliveResponseToProtocol( can_keep_alive )
                
                print(response)
                
                # translates the response protocol into bytes
                response_bytes = response.encode('ascii')
                
                # sends the response to the peer client
                self.socket.sendall( response_bytes )
                
            # Invalid request
            else:
                # creates a response containing "BAD REQUEST" status code
                response = ProtocolTranslator.leaveResponseToProtocol( False )
                
                print(response)
                
                # translates the response protocol into bytes
                response_bytes = response.encode('ascii')
                
                # sends the response to the peer client
                self.socket.sendall( response_bytes )
        
        # Exception occured (or timeout?) close tcp connection and return false                
        except:
            lock.release()
            self.socket.close()
            sys.exit()
            
        # Always close tcp connection socket before thread returns
        self.socket.close()
        

# initalize the list of peers
peer_list = PeerList()

# create a lock for the threads
lock = threading.Lock()

# using local for testing      
host = PeerUtils.getIPAddress()

print("Host: " + host )

# port the RS server listens on
port = 65243

# create a tcp socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind the tcp socket with its specific host and port
sock.bind((host, port))

# initialize a list of the peer threads
peer_threads = []

try:
    # while the server is running
    while True:

        # listen for new connections from peers
        sock.listen(5)

        # accept the connection from the client
        # retrieve the client socket, ip address, and port number sent
        (client_sock, (ip_addr, port)) = sock.accept()

        # obtain the new peer thread passing in the ip address, port number, and socket
        peer_thread = PeerThread(ip_addr, port, client_sock)

        # start this new peer thread
        peer_thread.start()

        peer_threads.append( peer_thread)

except KeyboardInterrupt:
    for peer_thread in peer_threads:
        peer_thread.join()

    print("\nRegistration System Exiting")
    sys.exit(1)

