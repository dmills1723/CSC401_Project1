import time
import math

class Node:
    # Initial
    def __init__(self, rfc_num, title, hostname, ttl=7200):
        self.rfc_num = rfc_num
        self.title = title
        self.hostname = hostname
        self.ttl = ttl
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

    # Get TTL of peer
    def get_ttl(self):
        return self.ttl

    # Get next node of linked list
    def get_next(self):
        return self.next

    # Reset TTL to 7200 seconds
    def reset_ttl(self, ttl=7200):
        self.ttl = ttl

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
        # self.ttl stores the time a PeerRecord will no longer be active,
        # rather than the actual TTL. The actuall TTL is calculated here
        # for the string representation.
        #if ( self.ttl < time.time() ) :
         #   ttl = 0
        #else :
            #ttl = self.ttl - time.time()
        #   ttl = math.ceil( self.ttl - time.time() )

        #lastRegistration_datetime = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime(self.lastRegistrationTime))

        #return ("RFC:%d\nTitle:%s\nHostname:%s\nTTL:%f"
        #       %( self.rfc_num, self.title, self.hostname, ttl, self.ttl ) )
        str_rfc = "RFC:" + str(self.rfc_num) + "\n"
        str_rfc += "Title:" + self.title + "\n"
        str_rfc += "Hostname:" + self.hostname + "\n"
        str_rfc += "TTL:" + str(self.ttl) + "\n"
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
            count = count + 1
            current = current.get_next()

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

    # Add node at the end of linked list
    def insert_end(self, rfc_num, title, hostname, ttl=7200):
        new = Node(rfc_num, title, hostname, ttl)

        if self.head is None:
            self.head = new
            return

        last = self.head

        while last.next:
            last = last.next

        last.next = new

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
    def add_sort(self, rfc_num, title, hostname, ttl=7200):
        current = self.head
        previous = None
        flag = False
        while current is not None and not flag:
            if current.get_rfc_num() > rfc_num:
                flag = True
            else:
                previous = current
                current = current.get_next()

        temp = Node(rfc_num, title, hostname, ttl)

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