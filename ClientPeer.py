from LinkedList import LinkedList
from RFCServer import RFCServer
from multiprocessing import Process, Pipe
import ProtocolTranslator
import PeerUtils
import sys
import time
import os
import signal
import socket
import numpy as np

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
        command = input('(1) Register, (2) DownloadRFC, (3) KeepAlive, (4) Leave:\n')
        if command == "Register":

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', RS_PORT))

            request = ProtocolTranslator.registerQueryToProtocol(HOST, rfc_server_port, cookie)
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
                print("You must Register first!\n")
                continue

            # PQuery: when a peer wishes to download a query, it first sends this query message to the RS (by
            # opening a new TCP connection), and in response it receives a list of active peers that includes
            # the hostname and RFC server port information.
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
            print( "success: %s" %success )

            global Peer_List
            if success:
                Peer_List = p_list

            ########################################################################
            ########################################################################
            ########################################################################
            ########################################################################

            global rfc
            rfc = 0
            # Ask user for specific RFC number and ensure it is an integer value
            while True:
                try:
                    rfc = int(input("Which RFC would you like to download?\n"))
                except ValueError:
                    print("That is not an integer!\n")
                    continue
                else:
                    break

            # Search RFC Index for RFC
            global RFC_index
            record = RFC_index.search(rfc)

            # First --> If RFC is found in local RFC Index
            if record is not None and Peer_List:
                # Client already owns the RFC file
                # (Found in RFC Index and we already own the RFC document)
                rfc_path = os.path.join(os.path.curdir, "RFCs", "rfc%s.txt" % rfc)
                hasLocalFile = os.path.isfile(rfc_path)

                if hasLocalFile :
                    print("RFC record is already available on this system!\n")
                    continue

                # find the port number of the peer in the peer list
                # open up a socket to this peer
                # send a request to the peer to get their RFC
                # receive the downloaded text file
                # Then --> GetRFC: a peer requests to download a specific RFC document from a remote peer.
                # (RFC document found in RFC Index, used hostname and Peer List to contact peer)
                else:
                    found = False
                    for peer in np.flip(Peer_List.peer_list):
                        if record.hostname == peer.hostname:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.connect((peer.hostname, peer.port))

                            request = ProtocolTranslator.getRfcQueryToProtocol(rfc)
                            print(request)
                            sock.send(request.encode('ascii'))

                            response_bytes = sock.recv(2048)
                            response = str(response_bytes.decode('ascii'))
                            print(response)

                            found, rfc_file = ProtocolTranslator.getRfcResponseToElements(response)
                            print(rfc_file)
                            sock.close()

                    # Peer with RFC document is found
                    if found is True:
                        print("We have found a peer with this RFC record!\n")
                return

            # If not found in local RFC Index - need to contact another peer to merge peer list
            # First --> RFCQuery: a peer requests the RFC index from a remote peer.
            # Then --> GetRFC: a peer requests to download a specific RFC document from a remote peer.
            # (RFC document NOT found in RFC Index, need to iteratively contact peers from Peer List and merge
            # RFC Indexes to find RFC document)
            elif record is None and Peer_List:
                flag = 0
                # Contact all peers in Peer List until RFC document identified in merged RFC Index
                for peer in np.flip(Peer_List.peer_list):
                    print('for loop\n')
                    print(peer.hostname)
                    print(peer.port)
                    print(peer.isActive)

                    if peer.isActive:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((peer.hostname, peer.port))

                        request = ProtocolTranslator.rfcqueryQueryToProtocol(peer.hostname)
                        print('REQUEST:')
                        print(request)

                        sock.send(request.encode('ascii'))
                        response_bytes = sock.recv(2048)
                        response = str(response_bytes.decode('ascii'))
                        print('RESPONSE:')
                        print(response)

                        b, rfc_idx = ProtocolTranslator.rfcQueryResponseToElements(response)

                        print('RFC INDEX:')
                        print(rfc_idx)

                        sock.close()

                        # Peer has non-empty RFC Index
                        if rfc_idx is not None:
                            print('RFC index not none\n')
                            RFC_index_head = RFC_index.merge_sort(RFC_index.head, rfc_idx.head)
                            RFC_index = LinkedList( RFC_index_head )
                            print('List merged\n')
                            print( RFC_index )

                            # Search RFC Index for RFC
                            rfc_record = RFC_index.search(rfc)
                            # RFC document found in newly merged RFC Index
                            if rfc_record is not None:
                                print('RFC is found\n')
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.connect((rfc_record.hostname, peer.port))

                                request = ProtocolTranslator.getRfcQueryToProtocol(rfc)
                                print(request)
                                sock.send(request.encode('ascii'))

                                response_bytes = sock.recv(2048)
                                response = str(response_bytes.decode('ascii'))
                                print(response)

                                found, rfc_file = ProtocolTranslator.getRfcResponseToElements(response)
                                PeerUtils.writeRFCFile(rfc_file, rfc)
                                sock.close()

                                # Peer contacted and RFC document received
                                if found is True and rfc_file is not None:
                                    print("We have found a peer and received the RFC document :)\n")
                                    flag = 1

                            # RFC NOT found in newly merged RFC Index - move onto to next peer
                            else:
                                print('no RFC found in RFC Index\n')
                                continue

                        # Peer has empty RFC Index
                        else:
                            print('empty RFC\n')
                            continue

                if flag == 0:
                    print("We have not found a peer with the RFC document :(\n")

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

            elif Peer_List is None:
                print('No Active Peers!\n')
                continue

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

        elif command == "peerlist" :
            print(Peer_List)
        elif command == "rfcindex" :
            print(RFC_index)
            
        elif command == "Exit" :

            break

    print("Successfully exited program\n")
    sys.exit(0)

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

# Adds its RFCs to the RFC index
RFC_index.add_sort(8540, 'Stream Control Transmission Protocol: Errata and Issues in RFC 4960', '127.0.0.1', 7200)

# RFC requested
rfc = 0

# Peer List for this client
Peer_List = None

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
RS_PORT = 65243

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

main_menu()
