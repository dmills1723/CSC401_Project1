from LinkedList import LinkedList
from RFCServer import RFCServer
from multiprocessing import Process, Pipe
import ProtocolTranslator
import time
import os
import signal
import socket

'''
   Waits for the RFCServer to gracefully terminate, then exits.
'''
def sigHandler(signum, frame) :
    server_proc.join()
    exit()
    
'''
    Merge sorted linked lists
'''
def merge_sort(self, list_1_head, list_2_head) :
    if list_1_head is None:
        return list_2_head
    if list_2_head is None:
        return list_1_head

    if list_2_head.rfc_num >= list_1_head.rfc_num:
        temp = list_1_head
        temp.next = self.merge_sort(list_1_head.next, list_2_head)
    else:
        temp = list_2_head
        temp.next = self.merge_sort(list_1_head, list_2_head.next)

    return temp


'''
    Creates an RFCServer and runs it. The RFCServer will listen for
    messages passed along the shared pipe. Objects (i.e. the RFCIndex)
    can be sent through this pipe.
    e.g. 
        in PeerClient:
            client_pipe.send( rfc_index )
        in RFCServer:
            rfc_index = server_pipe.rcv()
'''
def run_rfc_server(server_pipe, rfc_index):
    # Creates and starts RFCServer.
    rfc_server = RFCServer(server_pipe, rfc_index)
    rfc_server.run()


##### Register with RS. Send RFCServer port with this message.
##### Main menu prompt (could be : (1) downloadRFC, (2) keepalive, (3) register, (4) leave)


def main_menu():
    # Client cookie
    cookie = -1
    while True:
        try:
            command = input('(1) Register, (2) DownloadRFC, (3) KeepAlive, (4) Leave:\n')
            if command == "Register":

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('127.0.0.1', RS_PORT))

                request = ProtocolTranslator.registerQueryToProtocol(HOST, 11000, cookie)
                print(request)
                sock.send(request.encode('ascii'))

                response_bytes = sock.recv(2048)
                response = str(response_bytes.decode('ascii'))
                print(response)

                cookie = ProtocolTranslator.registerResponseToElements(response)
                sock.close()

            elif command == "DownloadRFC":

                # Check if unregistered client
                if cookie == -1:
                    print("You must Register first.\n")
                    return

                # Connect to RS and get peer list
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('127.0.0.1', RS_PORT))

                request = ProtocolTranslator.pqueryQueryToProtocol(cookie)
                print(request)

                sock.send(request.encode('ascii'))
                response = ''

                while True:
                    response_bytes = sock.recv(2048)
                    response += str(response_bytes.decode('ascii'))

                    if response[-4:] == "END\n":
                        break

                print(response)

                success, p_list = ProtocolTranslator.pqueryResponseToElements(response)

                global Peer_List
                if success:
                    Peer_List = p_list

                ########################################################################
                ########################################################################
                ########################################################################
                ########################################################################

                rfc = 0
                # Check RFC number is an integer value
                try:
                    rfc = input("Which RFC would you like to download?\n")
                except ValueError:
                    print("That is not an integer!\n")

                # first check merged RFC Index
                global RFC_index
                record = RFC_index.search(rfc)

                # If found in merged RFC Index
                if record is not None:
                    # Client already owns the RFC file
                    if record.hostname == HOST:
                        print("RFC record is already available on this system!\n")

                    # find the port number of the peer in the peer list
                    # open up a socket to this peer
                    # send a request to the peer to get their RFC
                    # receive the downloaded text file
                    else:
                        found = 0
                        for peer in Peer_List.peer_list:
                            if record.hostname == peer.hostname:
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.connect(('127.0.0.1', peer.port))

                                request = ProtocolTranslator.getRfcQueryToProtocol(rfc)
                                print(request)
                                sock.send(request.encode('ascii'))

                                response_bytes = sock.recv(2048)
                                response = str(response_bytes.decode('ascii'))
                                print(response)

                                rfc_file = ProtocolTranslator.getRfcResponseToElements(response)
                                print(rfc_file)
                                sock.close()

                                found = 1
                        if found == 1:
                            print("We have found a peer with this RFC record!\n")
                    return
                # If not found in merged RFC Index
                else:
                    flag = 0
                    for record in Peer_List.peer_list:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect(('127.0.0.1', RS_PORT))

                        request = ProtocolTranslator.rfcqueryQueryToProtocol(record.hostname)
                        print(request)

                        sock.send(request.encode('ascii'))
                        response_bytes = sock.recv(2048)
                        response = str(response_bytes.decode('ascii'))
                        print(response)

                        rfc_idx = ProtocolTranslator.rfcQueryResponseToElements(response)

                        if rfc_idx is not None:
                            RFC_index = LinkedList.merge_sort(RFC_index, rfc_idx)

                        sock.close()
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

                sock.close()

            elif command == "KeepAlive":

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('127.0.0.1', RS_PORT))

                request = ProtocolTranslator.keepAliveQueryToProtocol(cookie)
                print(request)
                sock.send(request.encode('ascii'))

                response_bytes = sock.recv(2048)
                response = str(response_bytes.decode('ascii'))
                print(response)
                ProtocolTranslator.keepAliveResponseToElements(response)

                sock.close()

            elif command == "Leave":

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('127.0.0.1', RS_PORT))

                request = ProtocolTranslator.leaveQueryToProtocol(cookie)
                print(request)
                sock.send(request.encode('ascii'))

                response_bytes = sock.recv(2048)
                response = str(response_bytes.decode('ascii'))
                print(response)
                ProtocolTranslator.leaveResponseToElements(response)

                sock.close()

            elif command == "Exit":

                print("Bye!\n")
                break

        except ValueError:
            print("Invalid Command\n")
            return True

## maintain cookie at all times (send cookie and RS returns cookie)

##### (1) downloadRFC: Ask user to specify a RFC to download
    ##### PQuery to RS for the PeerList
    ##### Iterate through PeerList. RFCQuery request to each peer's RFCServer for RFCIndex
        ##### Check if specified RFC is now in RFCIndex.
            ##### If so, start download with GetRFC request to peer's RFCServer
            ##### If not, report this to user and prompt again with main menu.
##### (2) keepalive
    ##### Signal RS to update TTL to keep alive

##### (3) register
    ##### Register to RS


#
# '''
#     TODO Infinite loop for now.
# '''
# def main_menu() :
#     while True :
#         time.sleep( 2 )

###### Build RFCIndex from local directory of RFCs TODO #######

RFC_index = LinkedList()

###### Start RFCServer as subprocess. #######

# Creates pipe for passing objects between parent and child process.
client_pipe, server_pipe = Pipe()

# Creates child process that runs "run_rfc_server()".
# Passes the RFC index to the child process on startup.


print("run_rfc_server: \n")
server_proc = Process(target=run_rfc_server, args=(server_pipe, RFC_index,))
server_proc.start()

# Sets signal handler function.
signal.signal(signal.SIGINT, sigHandler)

# Get the port the RFCServer is listening on. This blocks until a message arrives.
rfc_server_port = client_pipe.recv()

# When this client is finished, the RFC server is terminated.
# This could also be written so that the RFC server runs in
# the background after the client is terminated.

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
RS_PORT = 65243

# Peer List for this client
Peer_List = None

# Adds its RFCs to the RFC index
RFC_index.add_sort(8540, '127.0.0.1', 'Stream Control Transmission Protocol: Errata and Issues in RFC 4960', 7200)

main_menu()
