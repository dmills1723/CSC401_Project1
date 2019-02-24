from LinkedList import LinkedList
from RFCServer import RFCServer
from multiprocessing import Process, Pipe
import time
import socket
    
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
def run_rfc_server( server_pipe, rfc_index ) :
    # Creates and starts RFCServer.
    rfc_server = RFCServer( server_pipe, rfc_index )

###### Build RFCIndex from local directory of RFCs TODO #######
rfc_index = LinkedList()

###### Start RFCServer as subprocess. #######

# Creates pipe for passing objects between parent and child process.
client_pipe, server_pipe = Pipe()

# Creates child process that runs "run_rfc_server()".
# Passes the RFC index to the child process on startup. 
server_proc = Process( target=run_rfc_server, args=(server_pipe, rfc_index,))
server_proc.start()

# Get the port the RFCServer is listening on. This blocks until a message arrives.
rfc_server_port = client_pipe.recv()
print( rfc_server_port )

# When this client is finished, the RFC server is terminated.
# This could also be written so that the RFC server runs in
# the background after the client is terminated.
server_proc.join()
#server_proc.terminate()

##### Register with RS. Send RFCServer port with this message.
##### Main menu prompt (could be : (1) downloadRFC, (2) keepalive, (3) register, (4) leave)

##### (1) downloadRFC: Ask user to specify a RFC to download 
    ##### PQuery to RS for the PeerList 
    ##### Iterate through PeerList. RFCQuery request to each peer's RFCServer for RFCIndex 
        ##### Check if specified RFC is now in RFCIndex. 
            ##### If so, start download with GetRFC request to peer's RFCServer
            ##### If not, report this to user and prompt again with main menu.
