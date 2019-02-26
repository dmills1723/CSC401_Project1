from LinkedList import LinkedList
import ProtocolTranslator
rfc_index = LinkedList()

rfc_index.add_sort(8540, 'Stream Control Transmission Protocol: Errata and Issues in RFC 4960', '127.0.0.1', 7200)

rfc_index.add_sort(8541, 'TCP Connections', '127.0.0.1',  7200)

rfc_index.add_sort(8542,  'Networking 101', '127.0.0.1', 7200)


rfc_index_str = str(rfc_index)

#print(rfc_index_str)
rfc_index2 = LinkedList()


rfc_index2.add_sort(8540, 'Stream Control Transmission Protocol: Errata and Issues in RFC 4960', '127.0.0.1', 7200)

rfc_index2.add_sort(8541, 'TCP Connections', '127.0.0.1',  7200)

rfc_index2.add_sort(8542,  'Networking 101', '127.0.0.1', 7200)

rfc_index_str2 = str(rfc_index)

#print(rfc_index_str2)


merged_head = rfc_index.merge_sort(rfc_index.head, rfc_index2.head)

#urrent = merged_rfc_index
#while current:
#    print(current)
#    current = current.next

merged_rfc_index = LinkedList(merged_head)

#print(merged_rfc_index)

merged_rfc_index.remove_duplicates()

#print(merged_rfc_index)

#merged_rfc_index.remove_node( 8541, '127.0.0.1')

#print(merged_rfc_index)

response = ProtocolTranslator.rfcQueryResponseToProtocol(True, str(merged_rfc_index))

print(response)

status, new_rfc = ProtocolTranslator.rfcQueryResponseToElements(response)

#print(new_rfc)
merged_head = rfc_index.merge_sort(rfc_index.head, new_rfc.head)


new_rfc_index = LinkedList(merged_head)

#print(new_rfc_index)
new_rfc_index.remove_duplicates()

new_rfc_index.remove_node(8541, "127.0.0.1")

print(new_rfc_index)