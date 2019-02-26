
"""
Creates the RFC index for this Peer.
NOTE: Call this function on Peer startup
"""
def createRFCIndex(rfc_index):
    #TODO
    return
    # check if RFC directory exists

    # if not - creates this directory from current directory

    # if so - creates an RFC record for each document this Peer has in the RFC directory

"""
Downloads the RFC file this Peer Client received from another Peer Server.
"""
def downloadRFC( rfc_string ):
    #TODO
    return
    # opens a new file to the RFC directory

    # writes the string to the file with the name of rfc####.txt

    # also, needs to update RFC Index ( you now hold this RFC  )
