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


def sigHandler(signum, frame):
    server_proc.join()
    exit()


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


# Main menu prompt --> (1) Register, (2) PQuery (3) RFCQuery (4) DownloadRFC, (5) KeepAlive, (6) Leave, (7) Exit
def main_menu():
    # Client cookie
    cookie = -1
    while True:
        command = input('(1) Register, (2) PQuery (3) RFCQuery (4) DownloadRFC, (5) KeepAlive, (6) Leave, (7) Exit:\n')
        print('')
        if command == "Register":

            global leave_bool
            # Check if client has already registered
            if cookie != -1 and leave_bool is False:
                print("You have already Registered!\n")
                continue

            leave_bool = False

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((RS_HOST , RS_PORT))

            request = ProtocolTranslator.registerQueryToProtocol(HOST, rfc_server_port, cookie)
            print(request)
            sock.sendall(request.encode('ascii'))

            response_bytes = sock.recv(2048)
            response = str(response_bytes.decode('ascii'))
            print(response)

            cookie = ProtocolTranslator.registerResponseToElements(response)
            sock.close()

        elif command == "PQuery":

            # Check if unregistered client
            if cookie == -1 or leave_bool is True:
                print("You must Register first!\n")
                continue

            # PQuery: when a peer wishes to download a query, it first sends this query message to the RS (by
            # opening a new TCP connection), and in response it receives a list of active peers that includes
            # the hostname and RFC server port information.
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((RS_HOST, RS_PORT))

            request = ProtocolTranslator.pqueryQueryToProtocol(cookie)
            print(request)

            sock.sendall(request.encode('ascii'))
            response = ''

            while True:
                response_bytes = sock.recv(2048)
                response += str(response_bytes.decode('ascii'))

                if response[-4:] == "END\n":
                    break

            print(response)
            sock.close()
            list_success, p_list = ProtocolTranslator.pqueryResponseToElements(response)

            global Peer_List
            Peer_List = p_list

            print("-----------------------------------------------------------")
            print("ClientPeer peer_list: \n%s" % Peer_List)

        elif command == "RFCQuery":

            # Check if unregistered client
            if cookie == -1 or leave_bool is True:
                print("You must Register first!\n")
                continue

            if Peer_List is None or len(Peer_List.peer_list) == 0:
                print("There are no active peers to query!\n")
                continue

            # Contact all peers in Peer List until RFC document identified in merged RFC Index
            for peer in np.flip(Peer_List.peer_list):

                if peer.isActive:
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.connect((peer.hostname, peer.port))
                    except:
                        sock.close()
                        continue
                    request = ProtocolTranslator.rfcqueryQueryToProtocol(peer.hostname)
                    print(request)
                    sock.sendall(request.encode('ascii'))

                    response = ''

                    while True:
                        response_bytes = sock.recv(2048)
                        response += str(response_bytes.decode('ascii'))

                        if response[-4:] == "END\n":
                            break

                    print(response)

                    b, rfc_idx = ProtocolTranslator.rfcQueryResponseToElements(response)

                    sock.close()

                    global RFC_index
                    # Peer has non-empty RFC Index
                    if rfc_idx is not None:
                        RFC_index_head = RFC_index.merge_sort(RFC_index.head, rfc_idx.head)
                        RFC_index = LinkedList(RFC_index_head)
                        RFC_index.remove_duplicates()
                        client_pipe.send(RFC_index)
                        print("-----------------------------------------------------------")
                        print("ClientPeer RFC Index:\n")
                        print(RFC_index)

        elif command == "DownloadRFC":

            # Check if unregistered client
            if cookie == -1 or leave_bool is True:
                print("You must Register first!\n")
                continue

            # PQuery: when a peer wishes to download a query, it first sends this query message to the RS (by
            # opening a new TCP connection), and in response it receives a list of active peers that includes
            # the hostname and RFC server port information.
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((RS_HOST , RS_PORT))

            request = ProtocolTranslator.pqueryQueryToProtocol(cookie)
            print(request)

            sock.sendall(request.encode('ascii'))
            response = ''

            while True:
                response_bytes = sock.recv(2048)
                response += str(response_bytes.decode('ascii'))

                if response[-4:] == "END\n":
                    break

            print(response)
            sock.close()
            list_success, p_list = ProtocolTranslator.pqueryResponseToElements(response)

            Peer_List = p_list

            print("-----------------------------------------------------------")
            print("ClientPeer peer_list: \n%s" %Peer_List)

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
            record = RFC_index.search(rfc)

            # First --> If RFC is found in local RFC Index
            if record is not None and Peer_List:
                # Client already owns the RFC file
                # (Found in RFC Index and we already own the RFC document)
                rfc_path = os.path.join(os.path.curdir, "RFCs", "rfc%s.txt" % rfc)
                hasLocalFile = os.path.isfile(rfc_path)

                if hasLocalFile:
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
                        if record.hostname == peer.hostname and peer.isActive:
                            try:
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.connect((peer.hostname, peer.port))
                            except:
                                sock.close()
                                continue

                            request = ProtocolTranslator.getRfcQueryToProtocol(rfc)
                            print(request)
                            sock.sendall(request.encode('ascii'))

                            response = ''
                            while True:
                                response_bytes = sock.recv(2048)
                                response += str(response_bytes.decode('ascii'))

                                if response[-4:] == "END\n":
                                    break

                            print(response)

                            found, rfc_file = ProtocolTranslator.getRfcResponseToElements(response)
                            PeerUtils.writeRFCFile(rfc_file, rfc)

                            print( rfc_file )
                            sock.close()

                    # Peer with RFC document is found
                    if found is True:
                        print("We have found a peer and received the RFC document :)\n")
                continue

            # If not found in local RFC Index - need to contact another peer to merge peer list
            # First --> RFCQuery: a peer requests the RFC index from a remote peer.
            # Then --> GetRFC: a peer requests to download a specific RFC document from a remote peer.
            # (RFC document NOT found in RFC Index, need to iteratively contact peers from Peer List and merge
            # RFC Indexes to find RFC document)
            elif record is None and Peer_List:
                flag = 0

                # Contact all peers in Peer List until RFC document identified in merged RFC Index
                for peer in np.flip(Peer_List.peer_list):

                    if peer.isActive:
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.connect((peer.hostname, peer.port))
                        except:
                            sock.close()
                            continue
                        request = ProtocolTranslator.rfcqueryQueryToProtocol(peer.hostname)
                        print(request)
                        sock.sendall(request.encode('ascii'))

                        response = ''

                        while True:
                            response_bytes = sock.recv(2048)
                            response += str(response_bytes.decode('ascii'))

                            if response[-4:] == "END\n":
                                break

                        print(response)
                        #response_bytes = sock.recv(2048)
                        #response = str(response_bytes.decode('ascii'))
                        #print(response)

                        b, rfc_idx = ProtocolTranslator.rfcQueryResponseToElements(response)

                        sock.close()

                        # Peer has non-empty RFC Index
                        if rfc_idx is not None:
                            RFC_index_head = RFC_index.merge_sort(RFC_index.head, rfc_idx.head)
                            RFC_index = LinkedList(RFC_index_head)
                            RFC_index.remove_duplicates()
                            client_pipe.send(RFC_index)

                            # Search RFC Index for RFC
                            rfc_record = RFC_index.search(rfc)
                            # RFC document found in newly merged RFC Index
                            if rfc_record is not None:
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.connect((rfc_record.hostname, peer.port))

                                request = ProtocolTranslator.getRfcQueryToProtocol(rfc)
                                print(request)
                                sock.sendall(request.encode('ascii'))
                                response = ''

                                while True:
                                    response_bytes = sock.recv(2048)
                                    response += str(response_bytes.decode('ascii'))

                                    if response[-4:] == "END\n":
                                        break

                                print(response)
                                #response_bytes = sock.recv(2048)
                                #response = str(response_bytes.decode('ascii'))
                                #print(response)

                                found, rfc_file = ProtocolTranslator.getRfcResponseToElements(response)
                                PeerUtils.writeRFCFile(rfc_file, rfc)
                                sock.close()

                                # Peer contacted and RFC document received
                                if found is True and rfc_file is not None:
                                    print("We have found a peer and received the RFC document :)\n")
                                    flag = 1

                                    # Add node to RFC Index with num/title of RFC found, local host, and 7200 TTL
                                    RFC_index.add_sort(rfc, rfc_record.title, HOST, isLocal=True)
                                    client_pipe.send(RFC_index)

                            # RFC NOT found in newly merged RFC Index - move onto to next peer
                            else:
                                continue

                        # Peer has empty RFC Index
                        else:
                            continue

                if flag == 0:
                    print("We have not found a peer with the RFC document :(\n")

            elif Peer_List is None:
                print('No Active Peers!\n')
                continue

            #sock.close()

        elif command == "KeepAlive":

            # Check if unregistered client
            if cookie == -1 or leave_bool is True:
                print("You have not Registered yet!\n")
                continue

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((RS_HOST, RS_PORT))

            request = ProtocolTranslator.keepAliveQueryToProtocol(cookie)
            print(request)
            sock.sendall(request.encode('ascii'))

            response_bytes = sock.recv(2048)
            response = str(response_bytes.decode('ascii'))
            print(response)
            ProtocolTranslator.keepAliveResponseToElements(response)

            sock.close()

        elif command == "Leave":

            # Check if unregistered client
            if cookie == -1:
                print("You have not Registered yet!\n")
                continue

            if leave_bool is True:
                print("You have already left!\n")
                continue

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((RS_HOST, RS_PORT))

            request = ProtocolTranslator.leaveQueryToProtocol(cookie)
            print(request)
            sock.sendall(request.encode('ascii'))

            response_bytes = sock.recv(2048)
            response = str(response_bytes.decode('ascii'))
            print(response)
            ProtocolTranslator.leaveResponseToElements(response)

            leave_bool = True

            sock.close()

        elif command == "Exit":
            server_proc.terminate()
            break
        else:
            print("Invalid Command\n")

    print("Successfully exited program\n")
    sys.exit(0)


# Hostname for RS
RS_HOST = ''

# Localhost address for client
HOST = PeerUtils.getIPAddress()

# RS port
RS_PORT = 65243

# RFC Index for this client
RFC_index = LinkedList()

success, msg = PeerUtils.getRSHostname(sys.argv)

if success:
    RS_HOST = msg
else:
    print(msg)
    sys.exit(1)



# Adds its RFCs to the RFC index\
PeerUtils.createRFCIndex(RFC_index, HOST)

# RFC requested
rfc = 0

# Leave boolean, for clients who have left but not exited
# True if client has left, false if client has not
leave_bool = False

# Peer List for this client
Peer_List = None

# Start RFCServer as subprocess
# Creates pipe for passing objects between parent and child process.
client_pipe, server_pipe = Pipe()

# Creates child process that runs "run_rfc_server()".
# Passes the RFC index to the child process on startup.
server_proc = Process(target=run_rfc_server, args=(server_pipe, RFC_index,))
server_proc.start()

# Sets signal handler function.
signal.signal(signal.SIGINT, sigHandler)

# Get the port the RFCServer is listening on. This blocks until a message arrives.
rfc_server_port = client_pipe.recv()

# When this client is finished, the RFC server is terminated.
# This could also be written so that the RFC server runs in
# the background after the client is terminated.

# Start Main Menu for client user
main_menu()
