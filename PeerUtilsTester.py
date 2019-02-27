import PeerUtils
import ProtocolTranslator
from LinkedList import LinkedList

# Initializes the  RFC Index
rfc_index = LinkedList()

# Inserts all of the RFC Index records for this Peer from its RFCs directory
PeerUtils.createRFCIndex(rfc_index, '127.0.0.1')
# Displays its RFC Index (contains all 60 RFCs)
print(rfc_index)

# Creates a query for the RFC 8540
query = ProtocolTranslator.getRfcQueryToProtocol(8537)
print(query)

# Interprets the query for the RFC to obtain the RFC number
rfc_num = ProtocolTranslator.getRfcQueryToElements(query)

# Gets the text representation of this file for the requested RFC number
text = PeerUtils.getRFCFileText(rfc_num)

# Creates the response that contains the RFC file text
response = ProtocolTranslator.getRfcResponseToProtocol(True, text)
print(response)
# Obtains the RFC file text from the response sent
status, rfc_file_txt = ProtocolTranslator.getRfcResponseToElements(response)

print(rfc_file_txt)
# Writes the text to the new RFC file in their RFCs directory
# NOTE: Creating a temp rfc1111.txt to make sure the writing to file is working properly
PeerUtils.writeRFCFile(rfc_file_txt, 1111)
