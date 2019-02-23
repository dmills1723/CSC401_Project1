import time
import numpy 
import math

'''
    Defines a single record of the PeerList maintained by 
    the Registration Server.
'''
class PeerRecord:
    #TTL_DEFAULT = 7200
    TTL_DEFAULT = 5

    '''
        Creates a new PeerRecord.
        @param hostname (string) like "somehost.csc.ncsu.edu"
        @param cookie (integer) Unique ID for this peer.
        @param port (integer) port this peer's RFC server listens on
    '''
    def __init__( self, hostname, cookie, port ) :
        self.hostname = hostname
        self.cookie = cookie
        self.port = port
        self.timesActive = 0
        self.isActive = False
        self.lastRegistrationTime = 0
        self.register()
    
    '''
        Registers a peer with the Registration Server. If the peer already exists
        in the list, TODO
    '''
    def register( self ) :
        self.ttl = self.TTL_DEFAULT + time.time()
        # Registering while already active is ignored and 
        # treated as a KeepAlive call.
        if ( self.isActive == False ) :
            self.timesActive += 1
            self.lastRegistrationTime = time.time()
        self.isActive = True

    '''
        Returns whether this peer is currently active.
    '''
    def isPeerActive( self ) :
        currentTime = time.time()
        self.isActive = ( self.ttl > currentTime )
        return self.isActive 

    '''
        Returns a string representation of a PeerRecord.
    '''
    def __str__( self ) :
        # self.ttl stores the time a PeerRecord will no longer be active,
        # rather than the actual TTL. The actuall TTL is calculated here
        # for the string representation.
        if ( self.ttl < time.time() ) :
            ttl = 0
        else :
            #ttl = self.ttl - time.time()
            ttl = math.ceil( self.ttl - time.time() )

        lastRegistration_datetime = time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime(self.lastRegistrationTime))

        return ("Hostname:%s\nCookie:%s\nPort:%s\nTTL:%f\nActive:%s\n"
               "LastRegistered:%s\nTimesActiveInMonth:%d\n"
                %( self.hostname, self.cookie, self.port, ttl, self.isActive, 
                lastRegistration_datetime, self.timesActive ))

    '''
        Updates the "isActive" instance variable.
    '''
    def update( self ) :
        self.isActive = self.isPeerActive()

    ''' 
        Sets this PeerRecord to inactive status. 
    '''
    def leave( self ) :
        self.isActive = False
        self.ttl = time.time()

'''
    Defines the list of peers managed by the Registration Server.
'''
class PeerList:
    INITIAL_UID = 1000

    '''
        Initializes an empty linked list "peer_list".
    '''
    def __init__(self, peer_list=None ) :
        self.peer_list = None
        if peer_list is None :
            self.peer_list = numpy.array( [] )
        else :
            self.peer_list = peer_list
        self.nextUID = self.INITIAL_UID 

    '''
        Registers a new peer. The caller may optionally specify
        a cookie. There are three cases handled:
        1) The specified cookie corresponds to an existing peer 
           in the list. The peer is made active, and their TTL
           is reset to 7200s.
        2) The specified cookie doesn't correspond to an existing 
           peer in the list, -1 is returned. 
        3) The specified cookie is "-1" (new peer). A cookie is generated,
           the peer is added to the list, made active, and the cookie
           is returned.

        @param hostname (string) identifying peer like "somehost.csc.ncsu.edu"
        @param port (integer) for the port the peer's RFC server is listening.
    '''
    def register( self, hostname, port, cookie) :
        peer_rec = None 
        if ( cookie == -1 ) :
            cookie = self.nextUID
            self.nextUID += 1
            peer_rec = PeerRecord( hostname, cookie, port )
            self.peer_list = numpy.append( self.peer_list, [peer_rec] )
        else : 
            peer_rec = getPeerByCookie( cookie )
            peer_rec.register()
        return cookie

    '''
        Searches the PeerList for the PeerRecord associated with the specified 
        cookie. If one is found it is returned, otherwise "None" is returned.
    '''
    def getPeerByCookie( self, cookie ) :
        for peer_rec in self.peer_list :
            if ( peer_rec.cookie == cookie ) :
                return peer_rec
        # If no PeerRecord is associated with the specified cookie, None is returned.
        return None
 



    '''
        If the peer associated with the passed cookie is currently active,
        their TTL is updated. Note that register() is called, but in 
        PeerRecord.register(), if a peer is active, the function does not
        re-register them (incrementing # times registered, updating last registration
        time, etc.), it only updates the TTL. For valid keepalive requests (i.e. 
        currently active peers) True is returned.

        If the peer associated with cookie is inactive, the keepalive request is
        considered invalid and False is returned.

    '''
    def keepAlive( self, cookie ) :
        peer_rec = self.getPeerByCookie( cookie )

        # If no peer associated with cookie in list (invalid case).
        if ( peer_rec is None ) :
            return 0

        # If peer is active (valid case).
        elif peer_rec.isPeerActive() :
            peer_rec.register()
            return 1

        # If peer is inactive (invalid case).
        else : 
            return 2
       
    '''
        Returns a numpy array of the currently active peers. This array can be 
        "pickled", sent in the body of a PeerList Response message, "unpickled"
        and passed into the PeerList constructor to create a local PeerList.
    '''
    def pQuery( self, cookie ) :
        self.update()

        peer_list = numpy.array( [] )
        for peer_rec in self.peer_list :
            if ( peer_rec.isActive ) :
                peer_list = numpy.append( peer_list, [peer_rec])
        return peer_list

    '''
        Updates the isActive field of all peer records in the list. 
    '''
    def update( self ) :
        for peer_rec in self.peer_list :
            peer_rec.update()
        
    ''' 
        
    '''
    def leave( self, cookie ) :
        peer_rec = self.getPeerByCookie( cookie )
        peer_rec.leave()

    '''
        Returns a string representation of the PeerList, for printing 
        and debugging.
    '''
    def __str__( self ) :
        self.update()
        string_list = []
        for peer_rec in self.peer_list :
            string_list.append( str( peer_rec) )
        return '\n'.join( string_list )

