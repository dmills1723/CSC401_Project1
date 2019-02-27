import os
import socket

"""
Creates the RFC Index for this Peer for the passed in RFC index and hostname.
If the RFCs directory does not exist on this Peer - it will create this directory.
Otherwise, updates the RFC Index with all RFCs this Peer has in their RFCs directory.
NOTE: Call this function on PeerClient.py startup
"""
def createRFCIndex(rfc_index, hostname):
    # Checks if RFCs directory exists
    # Does not exits - creates the RFCs directory
    if not os.path.exists("RFCs"):
        os.mkdir("RFCs")

    # RFC directory exists
    # Creates an RFC record for each document this Peer has in the RFC directory
    else:
        path = "RFCs/"
        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)

            rfc_num = int(filename[3:7])
            file = open(filepath, "r")
            lines = file.readlines()

            idx = 0
            length = len(lines)
            while idx < length:
                if "Abstract" in lines[idx]:
                    break
                idx += 1
            idx = idx - 1
            title = ''
            title_found = False
            title_complete = False
            while not title_found or not title_complete:
                if not title_found and lines[idx] == '\n':
                    idx = idx - 1
                elif not title_found and lines[idx] != '\n':
                    title_found = True
                    title += lines[idx].strip()
                    idx = idx - 1
                elif not title_complete and lines[idx] != '\n':
                    temp = title
                    title = lines[idx].strip()
                    title = title + ' ' + temp
                    idx = idx - 1
                elif not title_complete and lines[idx] == '\n':
                    title_complete = True

            file.close()

            rfc_index.add_sort( rfc_num, title, hostname )

"""
Writes the RFC file this Peer Client received from another Peer Server
to the corresponding new file in their RFCs directory.
Takes in the RFC number and the string representation of this RFC file's 
text that was received from the other Peer as its parameters.
"""
def writeRFCFile( rfc_string, rfc_num ):
    path = "RFCs/"
    filepath = os.path.join(path, "rfc" + str(rfc_num) + ".txt" )
    file = open(filepath, "w+")

    file.write(rfc_string)

    file.close()

    # also, needs to update RFC Index ( you now hold this RFC  )

"""
Returns this RFC File's string representation for the passed in RFC number parameter.
"""
def getRFCFileText( rfc_num ):
    path = "RFCs/"
    filepath = os.path.join(path, "rfc" + str(rfc_num) + ".txt")
    file = open(filepath, "r")

    rfc_file_lines = file.read()
    file.close()

    return rfc_file_lines

''' 
Returns the IP address of this computer.
'''
def getIPAddress():
    # Creates socket to Google's nameserver.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))

    # Gets this computer's IP address from the socket connection.
    ip_addr = sock.getsockname()[0]

    sock.close()
    return ip_addr

"""
Gets the passed in Hostname for the RS from the Command Line Arguments.
If command line arguments invalid, returns False and a usage method.
If valid, returns True and the hostname of the RS server.
"""
def getRSHostname( sys_args ):

    if( len(sys_args) != 2):
        return False, "Usage: python3 ClientPeer.py <Hostname of RS Server>"

    hostname = sys_args[1]

    return True, hostname