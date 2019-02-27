import time
import math

class Node:
    TTL_DEFAULT = 7200
    # Initial
    def __init__(self, rfc_num, title, hostname, isLocal=False):
        self.rfc_num = rfc_num
        self.title = title
        self.hostname = hostname
        self.ttl = self.TTL_DEFAULT + time.time()
        self.isLocal = isLocal 
        self.next = None

    # Get RFC Number
    def get_rfc_num(self):
        return self.rfc_num

    # Get RFC Title
    def get_title (self):
        return self.title

    # Get Hostname of peer containing RFC
    def get_hostname(self):
        return self.hostname

    # Get next node of linked list
    def get_next(self):
        return self.next

    # Reset TTL to 7200 seconds
    def reset_ttl( self ):
        self.ttl = self.TTL_DEFAULT + math.floor( time.time() )

    # Set next node of linked list
    def set_next(self, new):
        self.next = new

    # Check if nodes in linked list have specific RFC number
    def has_value(self, rfc_num):
        if self.rfc_num == rfc_num:
            return True
        else:
            return False

    def __str__( self ) :
        str_rfc = "RFC:" + str(self.rfc_num) + "\n"
        str_rfc += "Title:" + self.title + "\n"
        str_rfc += "Hostname:" + self.hostname + "\n"
        return str_rfc


class LinkedList:
    # Initial
    def __init__(self, head=None):
        self.head = head

    # Print linked list in order
    def list_print(self):
        node = self.head

        while node:
            print(node.rfc_num)
            node = node.next

    # Size of linked list
    def size(self):
        count = 0
        current = self.head

        while current is not None:
            print( "infin loop" )
            count = count + 1
            #current = current.get_next()
            current = current.next

        return count

    # Search for node that has given rfc_num data
    def search(self, rfc_num):
        current = self.head
        flag = False
        while current is not None and flag is False:
            if current.get_rfc_num() == rfc_num:
                flag = True
            else:
                current = current.get_next()

        if current is None:
            return None

        return current

    # Remove node from linked list
    def remove_node(self, rfc_num, hostname):
        head = self.head
        #prev = None
        if head is not None:
            if head.rfc_num == rfc_num and head.hostname == hostname:
                self.head = head.next
                head = None
                return

        while head is not None:
            if head.rfc_num == rfc_num and head.hostname == hostname:
                break # exit loop
            prev = head
            head = head.next

        if head is None:
            return

        prev.next = head.next

    # Add nodes to list in sorted order
    def add_sort(self, rfc_num, title, hostname, ttl=7200, isLocal=False):
        current = self.head
        previous = None
        flag = False
        while current is not None and not flag:
            if current.get_rfc_num() > rfc_num:
                flag = True
            else:
                previous = current
                current = current.get_next()

        temp = Node(rfc_num, title, hostname, isLocal)

        if previous is None:
            temp.set_next(self.head)
            self.head = temp
        else:
            temp.set_next(current)
            previous.set_next(temp)

    # Remove duplicate nodes from linked list
    def remove_duplicates(self):
        current = self.head
        while current:
            if current.next and ( current.rfc_num == current.next.rfc_num ) and ( current.hostname == current.next.hostname ):
                if ( current.ttl >= current.next.ttl ) :
                    current.next = current.next.next
                else :
                    current.ttl = current.next.ttl
                    current.next = current.next.next
            current = current.next

    '''
        Returns a string representation of the PeerList, for printing 
        and debugging.
    '''
    def __str__( self ) :
        string_list = []
        current = self.head
        while current:
            string_list.append( str( current) )
            current = current.next
        return '\n'.join( string_list )

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
        Iterates through the RFC index and resets all local
        RFC index records to (TTL_DEFAULT + <seconds since epoch>)
    '''
    def update_ttls_for_rfcquery( self ) :
        current = self.head
        current_time = time.time()
        while current :
            if current.isLocal :
                current.reset_ttl()
                current.isLocal = False
                current = current.next
            elif ( current.ttl < current_time ) :
                temp = current
                current = current.next
                self.remove_node( temp.rfc_num, temp.hostname)
