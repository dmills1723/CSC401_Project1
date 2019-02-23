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


class LinkedList:
    # Initial
    def __init__(self):
        self.head = None

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
            last = last.nextval

        last.nextval = new

    # Remove node from linked list
    def remove_node(self, rfc_num):
        head = self.head

        if head is not None:
            if head.rfc_num == rfc_num:
                self.head = head.next
                head = None
                return

        while head is not None:
            if head.rfc_num == rfc_num:
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
            while current.next and current.rfc_num is current.next.rfc_num:
                current.next = current.next.next

            current = current.next
