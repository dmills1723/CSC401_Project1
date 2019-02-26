#!/usr/bin/env python3
from PeerList import PeerList
from PeerList import PeerRecord
from LinkedList import LinkedList
import numpy

"""

Static class for creating and translating protocols for this P2P-DI system. 
Contains functions for creating protocols that are to be sent to either a Peer or 
the Registration Server based on the given parameters. Also contains functions to 
translate recieved protocols back into their contained elements. 

"""


"""
Creates a register query for the Registration Server.
Requires the host, port, and cookie information be passed
into to this function. 
Returns the register query protocol string.
"""
def registerQueryToProtocol( host, port, cookie ):
    message = "Register\n"
    message += "Host:" + host + "\n"
    message += "Port:" + str(port) + "\n"
    message += "Cookie:" + str(cookie) + "\n"
    return message

"""
Obtains the elements contained within the register query protocol.
Returns the host name, port number, and cookie from this request.
"""
def registerQueryToElements( query ):
    lines = query.splitlines()
    host = lines[1].split(':')[1]
    port = int(lines[2].split(':')[1])
    cookie = int(lines[3].split(':')[1])
    
    return host, port, cookie

"""
Creates the register reponse to be sent back to the Peer client.
Takes in the cookie for this peer.
Returns the register response protocol string.
"""
def registerResponseToProtocol( cookie ):
    message = "OK 200\n"
    message += "Cookie:" + str(cookie) + "\n"
    return message

"""
Obtains the elements contained within the register response protocol.
Returns the cookie from this response.
"""
def registerResponseToElements( response ):
    lines = response.splitlines()
    cookie = int(lines[1].split(':')[1])
    return cookie

"""
Creates a pQuery query for the Registration Server.
Requires the peer's cookie be passed into the function
Returns the pQuery query protocol string.
"""
def pqueryQueryToProtocol( cookie ):
    message = "PQuery\n"
    message += "Cookie:" + str(cookie) + "\n"
    return message

"""
Obtains the elements contained within the pQuery query protocol.
Returns the cookie from this query.
"""
def pqueryQueryToElements( query ):
    lines = query.splitlines()
    cookie = int(lines[1].split(':')[1])
    return cookie

"""
Creates the pQuery reponse to be sent back to the Peer client.
Takes in a boolean value of whether this Peer's pQuery was successful and a String
representation of the the active Peer List users.
Returns the pQuery response protocol string with the corresponding status code.
"""
def pqueryResponseToProtocol(status, p_list):
    response = ''
    if status == 1:
        response += '200 OK\n'
    elif status == 0:
        response += '400 BAD REQUEST\n'
    elif status == 2:
        response += '300 NO ACTIVE PEERS\n'
    response += "Data:\n"
    response += p_list
    response += "END\n"
    return response

"""
Obtains the Peer List of active peers from the PQuery response protocol.
Returns a boolean value of True if the status was OK or False if it was 
a BAD REQUEST.
"""
def pqueryResponseToElements( response ):
    lines = response.splitlines()
    if lines[0] == '400 BAD REQUEST' or lines[0] == '300 NO ACTIVE PEERS':
        return False, None
    else:
        p_list = PeerList()
        current_idx = 2
        peer_idx = 0
        size = len(lines)
        while current_idx + 2 < size:
            hostname = lines[current_idx].split(':')[1]
            cookie = int(lines[current_idx+1].split(':')[1])
            port = int(lines[current_idx+2].split(':')[1])
            is_active = str_to_bool(lines[current_idx+4].split(':')[1])
            last_reg = float(lines[current_idx+5].split(':')[1])
            times_active = int(lines[current_idx+6].split(':')[1])
            
            record = PeerRecord(hostname, cookie, port, times_active, is_active, last_reg )
            p_list.peer_list = numpy.append( p_list.peer_list, [record])
            peer_idx += 1
            current_idx += 8
            
        return True, p_list
           

"""
Converts a string to its boolean value.
"""
def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False    
            

"""
Creates a leave query for the Registration Server.
Requires the peer's cookie be passed into the function.
Returns the leave query protocol string.
"""
def leaveQueryToProtocol( cookie ):
    message = "Leave\n"
    message += "Cookie:" + str(cookie) + "\n"
    return message

"""
Obtains the elements contained within the leave query protocol.
Returns the cookie from this query.
"""
def leaveQueryToElements( query ):
    lines = query.splitlines()
    cookie = int(lines[1].split(':')[1])
    return cookie
    
"""
Creates the leave reponse to be sent back to the Peer client.
Takes in a boolean value of whether this Peer's leave request was successful.
Returns the leave response protocol string with the corresponding status code.
"""
def leaveResponseToProtocol( can_leave ):
    response = ''
    if can_leave:
        response += '200 OK\n'
    else:
        response += '400 BAD REQUEST\n'
    return response

"""
Obtains the elements contained within the leave response protocol.
Returns a boolean value of True if the status was OK or False if it was 
a BAD REQUEST.
"""
def leaveResponseToElements( response ):
    if response == '200 OK\n':
        return True
    else:
        return False
        
"""
Creates a keepAlive query for the Registration Server.
Requires the peer's cookie be passed into the function.
Returns the keepAlive query protocol string.
"""
def keepAliveQueryToProtocol( cookie ):
    message = "KeepAlive\n"
    message += "Cookie:" + str(cookie) + "\n"
    return message

"""
Obtains the elements contained within the keepAlive query protocol.
Returns the cookie from this query.
"""
def keepAliveQueryToElements( query ):
    lines = query.splitlines()
    cookie = int(lines[1].split(':')[1])
    return cookie

"""
Creates the keepAlive reponse to be sent back to the Peer client.
Takes in a boolean value of whether this Peer's keepAlive request was successful.
Returns the keepAlive response protocol string with the corresponding status code.
"""
def keepAliveResponseToProtocol( can_keep_alive ):
    response = ''
    if can_keep_alive:
        response += '200 OK\n'
    else:
        response += '400 BAD REQUEST\n'
    return response
    
"""
Obtains the elements contained within the keepAlive response protocol.
Returns a boolean value of True if the status was OK or False if it was 
a BAD REQUEST.
"""
def keepAliveResponseToElements( response ):
    if response == '200 OK\n':
        return True
    else:
        return False

def rfcqueryQueryToProtocol( host ):
    message = "RFCQuery\n"
    message += "Host:" + host + "\n"
    return message

def rfcqueryQueryToElements( query ):
    lines = query.splitlines()
    host = lines[1].split(':')[1]
    return host

def rfcQueryResponseToProtocol( has_rfc_idx, rfc_idx_str ):
    response = ''
    if has_rfc_idx:
        response += '200 OK\n'
    else:
        response += '400 BAD REQUEST\n'
    response += "Data:\n"
    response += rfc_idx_str
    response += "END\n"
    return response

"""

Returns the RFC Index from the peer and boolean value of whether it exists.
NOTE: Only returns this peer's RFC Index. Inside ClientPeer.py - will need to merge with
own rfc_index, create new a linked list from the returned node, and then remove duplicates.

Example:
merged_head = rfc_index.merge_sort(rfc_index.head, peer_rfc_index.head)
merged_rfc_index = LinkedList(merged_head)
merged_rfc_index.remove_duplicates()

"""
def rfcQueryResponseToElements( response ):
    lines = response.splitlines()
    if lines[0] == '400 BAD REQUEST':
        return False, None
    else:
        peer_rfc_idx = LinkedList()
        current_idx = 2

        size = len(lines)
        while current_idx + 3 < size:
            rfc_num = int(lines[current_idx].split(':')[1])

            title_list = lines[current_idx + 1].split(':')
            length = len(title_list)
            idx = 1
            title = ''
            while( idx < length):
                title += title_list[idx]
                if(idx +1 < length):
                    title += ':'
                idx += 1
            hostname = lines[current_idx + 2].split(':')[1]
            ttl = float(lines[current_idx + 3].split(':')[1])

            peer_rfc_idx.add_sort(rfc_num, title, hostname, ttl)

            current_idx += 5

        return True, peer_rfc_idx

def getRfcQueryToProtocol( rfc ):
    message = "GetRFC\n"
    message += "RFC:" + str(rfc) + "\n"
    return message

def getRfcQueryToElements( query ):
    lines = query.splitlines()
    rfc_num = int(lines[1].split(':')[1])
    return rfc_num

def getRfcResponseToProtocol( has_file, rfc_file_text ):
    response = ''
    if has_file:
        response += '200 OK\n'
    else:
        response += '400 BAD REQUEST\n'
    response += "Data:\n"
    response += rfc_file_text
    response += "END\n"
    return response

def getRfcResponseToElements( response ):
    lines = response.splitlines()
    if lines[0] == '400 BAD REQUEST':
        return False, None
    else:
        # Might need to be more detailed than this but right not
        # just returning the rfc file as one string
        rfc_txt = lines[2]

        return True, rfc_txt

# Return for a request that doesn't match an expected request.
# Ideally, this shouldn't be called.
def genericBadRequestResponseToProtocol() :
        response = ''
        response += '400 BAD REQUEST\n'
        response += "Data:\n"
        response += "END\n"
        return response
