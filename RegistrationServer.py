#!/usr/bin/python3

import socket
import threading
import time


class PeerThread(threading.Thread):
    
    def __init__( self, ip_addr, port, socket ):
        threading.Thread.__init__(self)
        self.ip_addr = ip_addr
        self.port = port
        self.socket = socket
        # peer list object
        
        
    def run(self):
        try:
            # bytes sent from the peer
            data = self.socket.recv(2048)
            # convert bytes to string
            msg = str(data.decode('ascii'))
            # Peer sends the Register command
            if msg == "Register":
                # do the register method, port number
                # sends back cookie
                # Peer sends the Leave command
                return
            elif msg == "Leave":
                # always check if this peer exists first before processing other requests
                # sets flag in peer list to false
            # Peer sends the PQuery command
                return
            elif msg == "PQuery":
                # sends back a list of active peers that includes
                # the hostname and RFC server port information.
            # Peer sends the KeepAlive command
                return
            elif data == "KeepAlive":
                # upon receipt of this message, the RS resets the TTL value for this peer to 7200.
                return
            # Else invalid command
            else:
                #raise error('Error Processing Client request') 
                self.socket.close()
                return False                
        # Exception occured (or timeout?) close tcp connection and return false                
        except:
            self.socket.close()
            return False
        # Always close tcp connection socket before thread returns
        self.socket.close()
        
    def register(port_num):
        return None
        
    def leave():
        return None
    
    def peer_query():
        return None
    
    def keep_alive():
        return None

# using local for testing      
host = '127.0.0.1'

# port the RS server listens on
port = 65243

# create a tcp socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind the tcp socket with its specific host and port
sock.bind((host,port))

# initialize a list of the peer threads
peer_threads = []

# while the server is running
while True:

    start_time = time.time()
    
    # listen for new connections from peers
    sock.listen()
    
    # accept the connection from the client
    # retrieve the client socket, ip address, and port number
    (client_sock, (ip_addr, port)) = sock.accept()
    
    # obtain the new peer thread 
    peer_thread = PeerThread(ip_addr, port, client_sock)
    
    # start this new peer thread
    peer_thread.start()
    
    # append this peer thread to the list of peers
    peer_threads.append(peer_thread)
       
    # Q: where to decrement and check the TTL for all peers?
    # minus all TTL fields by amount of time passed (if peer is active)
    # if TTL is 0 or less -> change flag to inactive for the peer
    # might want a timeout for tcp connection to prevent blocking?
    elapsed_time = time.time() - start_time
    checkTTL(elapsed_time)
    
# terminate each thread in the list of peer threads
for thread in peer_threads:
    thread.join()
    
    
def checkTTL( elapsed_time ):
    return None
