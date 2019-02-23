#!/usr/bin/env python3

from PeerList import PeerList
import numpy
import math
import time

# Creating a new PeerList from scratch.
peer_list = PeerList()

print( "--------- Time 0: No Registered Peers ---------" )
print( peer_list )

peerAcookie = peer_list.register( "peerA", 333, -1)
time.sleep( 2 )

print( "--------- Time 2: PeerA Registered at Time 0 --------" )
print( peer_list )

peerBcookie = peer_list.register( "peerB", 444, -1)
time.sleep( 2 )

print( "--------- Time 4: PeerB Registered at Time 2 --------" )
print( peer_list )

peerCcookie = peer_list.register( "peerC", 555, -1)
time.sleep( 2 )

print( "--------- Time 6: PeerC Registered at Time 4, PeerA now inactive --------" )
print( peer_list )

print( "--------- Time 6: Active PeerList returned from pQuery --------" )
# Creating a new PeerList from the return of a pQuery().
    # This allows the Registration Server to pass the list returned from pQuery(), 
    # "active_peers", as a serialized/pickled object in the body of a "http" response,
    # and the client can construct a local copy of the RS's PeerList.
active_peers = peer_list.pQuery( 9999 )
active_peer_list = PeerList( active_peers )
print( active_peer_list )


