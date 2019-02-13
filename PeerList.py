import collections
import time

'''
    Defines a single record of the PeerList maintained by 
    the Registration Server.
'''
class PeerRecord:
    TTL_DEFAULT = 7200

    def __init__( self, hostname, cookie, port ) :
        self.hostname = hostname
        self.cookie = cookie
        self.port = port
        self.ttl = TTL_DEFAULT
        self.isActive = False
    
    def register() :
        self.lastRegistrationTime = time.time()
        self.ttl = TTL_DEFAULT
        self.isActive = True

    def isActive() :
        currentTime = time.time()
        timeElapsed = currentTime - self.lastRegistrationTime
        return ( timeElapsed > self.ttl )

'''
    Defines the list of peers managed by the 
    Registration Server.
'''
class PeerList:
    INITIAL_UID = 1000

    '''
        Initializes an empty linked list "peer_list".
    '''
    def __init__(self) :
        self.nextUID = INITIAL_UID
        self.peer_list = collections.deque()

    '''
        Adds a new peer record to the list. 
    '''
    def addPeer( self, hostname, port ) :
        cookie = self.nextUID

        newRecord = PeerRecord( hostname, cookie, port )
        self.nextUID += 1

        peer_list.append( newRecord )

        return cookie

