import socket
import ProtocolTranslator
from PeerList import PeerList
from LinkedList import LinkedList
import threading
import sys

"""
A thread that handles the tcp connection between a single Peer
and the Registration Server.
"""


class ServerThread(threading.Thread):
    """
    Constructor for this tcp connection with the peer.
    Sets the ip address, port number, and socket for
    this tcp connection.
    """

    def __init__(self, ip_addr, port, server_socket):
        threading.Thread.__init__(self, daemon=True)
        self.ip_addr = ip_addr
        self.port = port
        self.server_socket = server_socket
        self._is_running = True

    def stop(self):
        self._is_running = False

    """
    Handles the request protocl sent from the peer and
    sends back the approriate response protocol to this
    peer over this tcp connection.
    """

    def run(self):
        # while the server is running
        while self._is_running:
            # listen for new connections from peers
            self.server_socket.listen()

            # accept the connection from the client
            # retrieve the client socket, ip address, and port number sent
            (client_sock, (ip_addr, port)) = self.server_socket.accept()

            # obtain the new peer thread passing in the ip address, port number, and socket
            peer_thread = PeerThread(ip_addr, port, client_sock)

            # start this new peer thread
            peer_thread.start()


class PeerThread(threading.Thread):
    """
    Constructor for this tcp connection with the peer.
    Sets the ip address, port number, and socket for
    this tcp connection.
    """

    def __init__(self, ip_addr, port, socket):
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
            request = str(request_bytes.decode('ascii'))

            print(request)

            # obtains the method of this protocol
            method = request.splitlines()[0]

            # Peer sends the RFC QUERY REQUEST
            if method == "RFCQuery":
                return
            elif method == "GetRFC":
                return
            else:
                return

        # Exception occured (or timeout?) close tcp connection and return false
        except:
            #lock.release()
            self.socket.close()
            #sys.exit()

        # Always close tcp connection socket before thread returns
        self.socket.close()



def Main():

    # cmd lines arguments port number and RFCs
    # will grab specific RFCs from the RFCs folder and update its RFC_index
    # local host for testing
    #if( len(sys.argv) is not 2):
     #   print("Usage: python PeerClientTester.py <port number>")
      #  sys.exit(1)

    host = '127.0.0.1'
    #server_port = int(sys.argv[1])
    server_port = 12000
    # RS_port for connecting to the Registration Server
    RS_port = 65243
    # This client's cookie
    cookie = -1
    
    # Peer List for this client
    peer_list = None

    # RFC Index for this client
    RFC_index = LinkedList()

    # Adds its RFCs to the RFC index
    RFC_index.add_sort( 8540, '127.0.0.1', 'Stream Control Transmission Protocol: Errata and Issues in RFC 4960', 7200 )

    # create server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind the tcp socket with its specific host and port
    server_sock.bind((host, server_port))

    # obtain the new peer thread passing it the ip address, port number, and socket
    server_thread = ServerThread(host, server_port, server_sock)

    # start this new peer thread
    server_thread.start()


    while True:

        cmd = input("Enter Command: ")
        print()
        
        if cmd == "Register":

            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            s.connect((host,RS_port))
            
            request = ProtocolTranslator.registerQueryToProtocol( host, 11000, cookie )
        
            print(request)
        
            s.send(request.encode('ascii')) 

            response_bytes = s.recv(2048) 

            response = str(response_bytes.decode('ascii'))
     
            print(response) 
        
            cookie = ProtocolTranslator.registerResponseToElements( response )
        
            s.close()
            
        elif cmd == "PQuery":
            
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            s.connect((host,RS_port))
            
            request = ProtocolTranslator.pqueryQueryToProtocol( cookie )
        
            print(request)
        
            s.send(request.encode('ascii')) 
            response = ''
            while True:
                response_bytes = s.recv(2048) 

                response += str(response_bytes.decode('ascii'))

                if response[-4:] == "END\n":
                    break
        
            print(response)
     
            success, p_list = ProtocolTranslator.pqueryResponseToElements( response )
            
            if success:
                peer_list = p_list

            s.close()
        
        elif cmd == "Leave":
        
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            s.connect((host,RS_port))
            
            request = ProtocolTranslator.leaveQueryToProtocol( cookie )
        
            print(request)
        
            s.send(request.encode('ascii')) 
            
            response_bytes = s.recv(2048) 

            response = str(response_bytes.decode('ascii'))
     
            print(response) 
        
            status = ProtocolTranslator.leaveResponseToElements( response )
            
            #if status == True:
                #cookie = -1
            
            s.close()

        elif cmd == "KeepAlive":
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            s.connect((host,RS_port))
            
            request = ProtocolTranslator.keepAliveQueryToProtocol( cookie )
        
            print(request)
        
            s.send(request.encode('ascii')) 
            
            response_bytes = s.recv(2048) 

            response = str(response_bytes.decode('ascii'))
     
            print(response) 
        
            status = ProtocolTranslator.keepAliveResponseToElements( response )
            
            s.close()
        elif cmd == "GetRFC":
            if cookie == -1:
                print("Must Register first.\n")

            rfc = input("Which RFC would you like to download?")
            # need a check to make sure the rfc is an integer value

            # first checks RFC Index for that RFC
            record = RFC_index.search(rfc)

            if record is not None:
                # find the port number of the peer in the peer list
                # open up a socket to this peer
                # send a request to the peer to get their RFC
                # receive the downloaded text file
                print("There is a peer with this record")
                return
            else:
                for record in peer_list.peer_list:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((record.hostname, record.port))

                    request = ProtocolTranslator.rfcqueryQueryToProtocol(record.hostname)

                    print(request)

                    s.send(request.encode('ascii'))

                    response_bytes = s.recv(2048)

                    response = str(response_bytes.decode('ascii'))

                    print(response)

                    rfc_idx = ProtocolTranslator.rfcQueryResponseToElements(response)

                    if rfc_idx is not None:
                        RFC_index = LinkedList.merge_sort( RFC_index, rfc_idx)

                    s.close()
                    # iterate through the peers in the peer list
                    # open a socket to this peer
                    # send a request to the peer to get their rfc index
                    # merge index with own index
                    # check the rfc index again
                    # if rfc index now has the RFC wanted
                    # break out of this loop and send a get RFC request to this peer
                    # continue to next peer in the peer list

                # if file is not found after going through all active peers
                # return a message that the file does not exist
        elif cmd == "Exit":
            server_thread.stop()
            server_sock.close()
            break
        else:
            print("Invalid Command\n")

if __name__ == '__main__': 
    Main()
