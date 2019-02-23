from LinkedList import LinkedList
import socket
import threading
import sys


HOST = socket.gethostname()
PORT = 4200


class Client(threading.Thread):
    # Initial
    def __init__(self, port, ip_addr, sock=None):
        threading.Thread.__init__(self)
        self.ip_addr = ip_addr
        self.port = port
        if sock is None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.socket = sock

        self.PeerList = []
        self.RFCIndex = LinkedList()

    # Merge sorted linked lists
    def merge_sort(self, list_1_head, list_2_head):
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
